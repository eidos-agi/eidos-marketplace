# tint: tag -> color. The only file with real logic.
#
# Design constraints, in priority order:
#   1. STABLE  -- a tag's color must never change once you've learned it.
#   2. DISTINCT -- two tags you see side by side must not look alike.
#   3. DUMB    -- no model, no daemon, no network, sub-millisecond.
#
# (1) and (2) fight each other: maximizing distance across N tags means
# recomputing when N grows, which moves colors. We resolve it by assigning
# greedily and PERSISTING: a new tag takes the most-distant free hue and keeps
# it forever. Existing tags are never recomputed.

TINT_STATE=${TINT_STATE:-${XDG_CONFIG_HOME:-$HOME/.config}/tint/assigned.tsv}
TINT_OVERRIDES=${TINT_OVERRIDES:-${XDG_CONFIG_HOME:-$HOME/.config}/tint/overrides.tsv}

# Fixed saturation/lightness: vivid enough to tell apart, dark enough that the
# dimmed background keeps text readable. Only hue varies, which is why
# "maximize perceptual distance" collapses to "maximize hue separation" and we
# don't need a Lab colorspace conversion.
# ponytail: C and M are precomputed from S=0.72 L=0.58 since they never vary.
# ponytail: -g is load-bearing. Plain `typeset -F` makes these LOCAL when this
# file is sourced from inside a function (lazy-loaders do this), so they vanish
# and every colour silently computes to black. Caught by test/stress.zsh.
typeset -gF _TINT_C=0.6048   # (1 - |2L-1|) * S
typeset -gF _TINT_M=0.2776   # L - C/2

zmodload zsh/mathfunc   # int(), abs(), floor() -- not builtin to zsh arithmetic

_tint_hue2rgb() {  # hue(0-359) -> "R G B"
  local -F h=$1 hp x a hm2 r g b
  hp=$(( h / 60.0 ))
  local -i seg=$(( int(hp) % 6 ))
  hm2=$(( hp - 2*floor(hp/2) ))
  a=$(( abs(hm2 - 1) ))
  x=$(( _TINT_C * (1 - a) ))
  case $seg in
    0) r=$_TINT_C; g=$x;       b=0 ;;
    1) r=$x;       g=$_TINT_C; b=0 ;;
    2) r=0;        g=$_TINT_C; b=$x ;;
    3) r=0;        g=$x;       b=$_TINT_C ;;
    4) r=$x;       g=0;        b=$_TINT_C ;;
    5) r=$_TINT_C; g=0;        b=$x ;;
  esac
  printf '%d %d %d' $(( int((r+_TINT_M)*255 + 0.5) )) \
                    $(( int((g+_TINT_M)*255 + 0.5) )) \
                    $(( int((b+_TINT_M)*255 + 0.5) ))
}

# SMARTS, THE DUMB KIND: the name usually already says the colour.
# "greenmark" must be GREEN. Nobody accepts a magenta greenmark, and no model is
# needed to know that -- it's spelled out. Same trick as the rest of tint: read
# the label the human already wrote instead of inferring one.
# ponytail: a lookup table, not NLP. Unmatched names fall through to assignment.
typeset -gA _TINT_WORDS=(
  red 0      crimson 350 ruby 355  rose 340  pink 330  magenta 300
  coral 15   rust 20    orange 30  amber 45  sand 40   gold 50
  yellow 60  olive 80   lime 90    green 120 emerald 150 mint 160
  jade 155   teal 170   aqua 185   cyan 180  sky 205   azure 200
  navy 230   blue 240   indigo 260 violet 280 purple 285 lavender 275
  plum 295   slate 215  steel 210  forest 130 sage 110  moss 100
)

# Colours that are NOT a hue. The wheel is hue-only at fixed S/L, so it can make
# a vivid orange but never a brown -- brown IS dark desaturated orange, i.e. the
# two dimensions the wheel throws away. Brand colours live here as exact rgb.
# ponytail: a second tiny table beats generalising the whole palette to HSL.
typeset -gA _TINT_RGBWORDS=(
  brown  "150 96 56"    tan    "196 147 90"   beige "214 184 143"
  cream  "232 220 196"  sand   "205 175 125"  khaki "179 158 108"
  chocolate "108 68 40" coffee "120 88 64"    rust  "168 84 40"
  charcoal "90 86 80"   stone  "140 134 124"  bone  "222 214 198"
)

_tint_hex2rgb() {  # #rrggbb -> "R G B"
  local h=${1#\#}
  # ponytail: =~ regex, NOT the (#c6) glob -- that needs EXTENDED_GLOB, which
  # `emulate -L zsh` in bin/tint turns off, so every hex was silently rejected.
  [[ "$h" =~ '^[0-9a-fA-F]{6}$' ]] || return 1
  printf '%d %d %d' $(( 16#${h[1,2]} )) $(( 16#${h[3,4]} )) $(( 16#${h[5,6]} ))
}

# word -> "R G B" for any known colour word, hue-based or not.
_tint_rgb_from_word() {
  local w=${1:l}
  [[ -n "${_TINT_RGBWORDS[$w]}" ]] && { echo "${_TINT_RGBWORDS[$w]}"; return 0 }
  local h; h=$(_tint_hue_from_name "$w") && { _tint_hue2rgb $h; return 0 }
  return 1
}

# Longest match wins, so "forest" beats "rose" inside "forestrose".
_tint_hue_from_name() {
  local n=${1:l} w best="" bestlen=0
  for w in ${(k)_TINT_WORDS}; do
    [[ "$n" == *"$w"* ]] && (( ${#w} > bestlen )) && { best=$w; bestlen=${#w} }
  done
  [[ -n "$best" ]] && { echo ${_TINT_WORDS[$best]}; return 0 }
  return 1
}

# Given already-used hues, return the hue furthest from all of them.
# First tag gets 0; each subsequent tag lands in the widest remaining gap.
_tint_pick_hue() {
  local -a used=("$@")
  local -i h best=0 bestd=-1 d mind u
  (( ${#used} == 0 )) && { echo 0; return }
  for (( h=0; h<360; h+=3 )); do
    mind=360
    for u in "${used[@]}"; do
      d=$(( (h - u) % 360 )); (( d < 0 )) && d=$(( d + 360 ))
      (( d > 180 )) && d=$(( 360 - d ))
      (( d < mind )) && mind=$d
    done
    (( mind > bestd )) && { bestd=$mind; best=$h }
  done
  echo $best
}

# A tag is a TSV key, so it must not contain tabs/newlines or it corrupts the
# state file and silently loses every row after it.
_tint_clean() {
  local t=${1//[$'\t\n\r']/-}
  t=${t## }; t=${t%% }
  printf '%s' "$t"
}

_tint_state_get() {  # tag -> "hue" or empty
  [[ -f $TINT_STATE ]] || return 1
  local t hue
  while IFS=$'\t' read -r t hue; do
    # ponytail: strip CR. A state file synced from/edited on another machine has
    # CRLF, and the trailing ^M turns the hue into "90\r" -> bad math expression.
    hue=${hue%$'\r'}
    [[ "$hue" == <-> ]] || continue                # skip malformed/garbage rows
    [[ "$t" == "$1" ]] && { echo "$hue"; return 0 }
  done < $TINT_STATE
  return 1
}

# ponytail: mkdir is atomic, so it's the whole lock. You run many Claude sessions
# at once; without this they all read an empty state and pick the same hue.
# Falls through after ~1s rather than hanging a hook -- worst case is a colour
# collision, never a stalled prompt.
_tint_lock() {
  local lk="${TINT_STATE}.lock" i age
  for (( i=0; i<50; i++ )); do
    mkdir "$lk" 2>/dev/null && return 0
    # A holder that crashed would otherwise cost every future call the full
    # timeout, forever. Reap anything older than 10s.
    if [[ -d "$lk" ]]; then
      zmodload -F zsh/stat b:zstat 2>/dev/null
      zmodload zsh/datetime 2>/dev/null
      age=$(( EPOCHSECONDS - $(zstat +mtime "$lk" 2>/dev/null || print $EPOCHSECONDS) ))
      (( age > 10 )) && rmdir "$lk" 2>/dev/null
    fi
    sleep 0.02
  done
  return 1
}
_tint_unlock() { rmdir "${TINT_STATE}.lock" 2>/dev/null }

# Assign (and persist) a hue for a tag. Never reassigns an existing tag.
_tint_hue_for_tag() {
  local tag=$(_tint_clean "$1") hue
  hue=$(_tint_state_get "$tag") && { echo "$hue"; return 0 }
  mkdir -p ${TINT_STATE:h} 2>/dev/null || return 1
  _tint_lock
  # Re-check under the lock: someone may have assigned it while we waited.
  if hue=$(_tint_state_get "$tag"); then _tint_unlock; echo "$hue"; return 0; fi
  # The name wins over the algorithm: greenmark is green, full stop. Persisted
  # like any other assignment, so later tags route AROUND it and nothing else
  # steals green.
  if ! hue=$(_tint_hue_from_name "$tag"); then
    local -a used=()
    [[ -f $TINT_STATE ]] && used=( ${(f)"$(cut -f2 $TINT_STATE 2>/dev/null | grep -E '^[0-9]+$')"} )
    hue=$(_tint_pick_hue "${used[@]}")
  fi
  # ponytail: append-only tsv, not a db. Delete a line to re-roll one tag.
  printf '%s\t%s\n' "$tag" "$hue" >> $TINT_STATE
  _tint_unlock
  echo $hue
}

# tag -> "R G B". Honors overrides.tsv (tag<TAB>R G B, or tag<TAB>none).
tint_color_for_tag() {
  local tag=$(_tint_clean "$1") ov
  [[ -z "$tag" ]] && return 1
  if [[ -f $TINT_OVERRIDES ]]; then
    while IFS=$'\t' read -r t v; do
      [[ "$t" == "$tag" ]] && { ov="$v"; break }
    done < $TINT_OVERRIDES
  fi
  # ponytail: sentinel is the word "none", NOT "-" -- zsh's echo eats a lone "-"
  # as an end-of-options marker and it silently reads as "no override set".
  [[ "$ov" == "none" ]] && return 1
  [[ -n "$ov" ]] && { echo "$ov"; return 0 }
  _tint_hue2rgb $(_tint_hue_for_tag "$tag")
}

# Window bg = the tag colour pushed toward the theme's background, so text stays
# readable. One table, not two.
#   TINT_MODE=dark  (default) -> dim toward black
#   TINT_MODE=light           -> wash toward white
# ponytail: a dark tint on a light theme makes dark text unreadable -- that's the
# whole tool broken for light-theme users, so mode is a real setting, not polish.
: ${TINT_DIM:=13}
: ${TINT_MODE:=dark}
tint_bgtint_for_tag() {
  local rgb=$(tint_color_for_tag "$1") r g b
  [[ -z "$rgb" ]] && return 1
  read r g b <<< "$rgb"
  if [[ "$TINT_MODE" == "light" ]]; then
    # keep TINT_DIM% of the hue, rest white
    r=$(( r*TINT_DIM/100 + 255*(100-TINT_DIM)/100 ))
    g=$(( g*TINT_DIM/100 + 255*(100-TINT_DIM)/100 ))
    b=$(( b*TINT_DIM/100 + 255*(100-TINT_DIM)/100 ))
  else
    r=$((r*TINT_DIM/100)); g=$((g*TINT_DIM/100)); b=$((b*TINT_DIM/100))
  fi
  (( r>255 )) && r=255; (( g>255 )) && g=255; (( b>255 )) && b=255
  printf '#%02x%02x%02x' $r $g $b
}

# Emit iTerm2 tab + window-bg escapes for a tag. Caller redirects to a tty.
#   OSC 6  = iTerm2 tab color (proprietary)
#   OSC 11 = default background. It slips under a full-screen TUI because it
#            redefines what "background" MEANS rather than painting anything.
# $1 = name (text), $2 = group (colour). Group defaults to name.
tint_emit() {
  local grp=${2:-$1}
  local rgb=$(tint_color_for_tag "$grp")
  if [[ -z "$rgb" ]]; then
    printf '\033]6;1;bg;*;default\a\033]111\a'
  else
    printf '\033]6;1;bg;red;brightness;%s\a\033]6;1;bg;green;brightness;%s\a\033]6;1;bg;blue;brightness;%s\a' ${=rgb}
    printf '\033]11;%s\a' "$(tint_bgtint_for_tag "$grp")"
  fi
  # TINT IS THE HINT, THE NAME IS THE GAME -- but tint doesn't have to be the one
  # who names it. OSC 1 (tab title) only. NOT OSC 2 (window title):
  #
  # Measured, not guessed: Claude Code repaints the window title continuously with
  # the live task ("Build iTerm2 window colour changer"). tint always loses that
  # race, and it SHOULD -- a natural-language task beats an org slug. Fighting for
  # OSC 2 replaced better information with worse and didn't even win.
  #
  # OSC 1 is free: hosts that also set it just overwrite us (harmless no-op), and
  # where nobody claims it, the tab bar carries the tag -- which is exactly when
  # you have many tabs and actually need the label. In tmux the name is not a
  # fight at all; see tint_apply.
  [[ -n "$1" && "$TINT_TITLE" != "0" ]] && printf '\033]1;%s\a' "$1"
  return 0
}

# Apply a tag to the current window. tmux and a bare terminal are different
# machines: inside tmux the escapes never reach the emulator (allow-passthrough
# is off by default), but tmux exposes the same two capabilities natively.
# ponytail: use tmux's own commands rather than DCS-wrapping escapes and asking
# the user to flip allow-passthrough.
# $1 = name (the game, shown as text), $2 = group (the hint, drives the colour)
tint_apply() {
  local tag=$1 grp=${2:-$1} tty=$3 bg
  if [[ -n "$TMUX" && -n "$TMUX_PANE" ]] && command -v tmux >/dev/null 2>&1; then
    bg=$(tint_bgtint_for_tag "$grp")
    if [[ -n "$bg" ]]; then
      tmux set -p -t "$TMUX_PANE" window-style "bg=$bg" 2>/dev/null
      # automatic-rename defaults ON and would overwrite the name instantly.
      tmux set -w -t "$TMUX_PANE" automatic-rename off 2>/dev/null
      tmux rename-window -t "$TMUX_PANE" "$tag" 2>/dev/null
    else
      tmux set -p -t "$TMUX_PANE" -u window-style 2>/dev/null
      # ponytail: unsetting automatic-rename is NOT enough -- tmux never
      # retroactively re-renames, so the window would keep a stale tag name
      # forever after you leave the topic. A wrong name is worse than no name,
      # so restore tmux's own default explicitly before handing the option back.
      tmux rename-window -t "$TMUX_PANE" '#{pane_current_command}' 2>/dev/null
      tmux set -w -t "$TMUX_PANE" -u automatic-rename 2>/dev/null
    fi
    return 0
  fi
  # ponytail: probe by OPENING, not by [[ -w ]]. /dev/tty is crw-rw-rw- so it
  # always looks writable, but the open fails when there's no controlling
  # terminal -- and that error escapes 2>/dev/null (the redirect is set up before
  # stderr is), printing "device not configured" into every non-interactive shell
  # that sources us. Reordering the redirects does NOT fix it; only a probe does.
  [[ -n "$tty" ]] || return 1
  ( exec 3>"$tty" ) 2>/dev/null || return 1
  tint_emit "$tag" "$grp" > "$tty" 2>/dev/null
  return 0
}
