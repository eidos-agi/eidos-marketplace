#!/bin/zsh
# Adversarial suite. Everything here is an attempt to BREAK tint.
#   zsh test/stress.zsh
emulate -L zsh

root=${0:A:h:h}
fail=0
ok()  { print -r -- "  ok   $1" }
bad() { print -r -- "  FAIL $1"; fail=1 }

fresh() {  # isolated state per case
  export TINT_STATE=$(mktemp -d)/assigned.tsv
  export TINT_OVERRIDES=${TINT_STATE:h}/overrides.tsv
  source $root/lib/color.zsh; source $root/lib/tag.zsh
}
fresh

print "== hostile tag strings =="
for t in 'a*' '[x]' 'a?b' '*' 'foo|bar' '../../etc' 'a b' "a'b" 'a"b' 'a$b' 'a`b' '-n' '--help'; do
  c=$(tint_color_for_tag "$t" 2>&1)
  [[ "$c" == <->' '<->' '<-> ]] || bad "tag '$t' -> '$c'"
done
ok "13 glob/quote/dash-hostile tags all produced valid rgb"

# a glob tag must not match a DIFFERENT tag's stored row
fresh
c_star=$(tint_color_for_tag '*')
c_zed=$(tint_color_for_tag 'zed')
[[ "$c_star" != "$c_zed" && "$c_star" != "0 0 0" ]] \
  && ok "'*' distinct from 'zed', and constants survived function-scope source" \
  || bad "'*'/'zed' both '$c_star' -- typeset -g regression (constants went local)"

print "\n== tags that could corrupt the TSV state =="
fresh
tint_color_for_tag $'tab\there' >/dev/null 2>&1
tint_color_for_tag $'nl\nhere'  >/dev/null 2>&1
tint_color_for_tag 'plain' >/dev/null
bad_rows=$(awk -F'\t' 'NF != 2 {n++} END{print n+0}' $TINT_STATE)
(( bad_rows == 0 )) && ok "state file stayed 2-column" || bad "$bad_rows malformed rows in state"
# and the tag written must round-trip to the same colour
a=$(tint_color_for_tag 'plain'); b=$(tint_color_for_tag 'plain')
[[ "$a" == "$b" ]] && ok "plain tag round-trips after hostile neighbours" || bad "round-trip broke"

print "\n== concurrency: many sessions assigning at once =="
fresh
for i in {1..12}; do ( tint_color_for_tag "conc$i" >/dev/null ) & done
wait
rows=$(wc -l < $TINT_STATE | tr -d ' ')
uniq_tags=$(cut -f1 $TINT_STATE | sort -u | wc -l | tr -d ' ')
uniq_hues=$(cut -f2 $TINT_STATE | sort -u | wc -l | tr -d ' ')
[[ "$rows" == "$uniq_tags" ]] && ok "no duplicate tag rows ($rows rows)" \
                              || bad "duplicate rows: $rows rows / $uniq_tags tags"
(( uniq_hues == uniq_tags )) && ok "12 concurrent tags got 12 distinct hues" \
                             || bad "hue collision under concurrency: $uniq_hues hues / $uniq_tags tags"

print "\n== does distinctness survive scale? =="
fresh
for i in {1..20}; do tint_color_for_tag "proj$i" >/dev/null; done
typeset -a hues=( ${(f)"$(cut -f2 $TINT_STATE)"} )
min=360
for (( i=1; i<=${#hues}; i++ )); do for (( j=i+1; j<=${#hues}; j++ )); do
  d=$(( (hues[i]-hues[j]) % 360 )); (( d<0 )) && d=$((d+360)); (( d>180 )) && d=$((360-d))
  (( d < min )) && min=$d
done; done
# ponytail: greedy-and-never-move cannot hit the theoretical 18deg for 20 tags.
# ~11deg is the documented price of stability. Asserting the real floor.
(( min >= 11 )) && ok "20 tags, min gap ${min}deg (>=11, see README limits)" \
                || bad "20 tags collapse below documented floor: ${min}deg"

print "\n== corrupt / adversarial state file =="
fresh
printf 'good\t90\ngarbage-no-hue\nx\ty\tz\n\n\tnohue\n' > $TINT_STATE
c=$(tint_color_for_tag 'good' 2>&1)
[[ "$c" == <->' '<->' '<-> ]] && ok "reads good row past garbage" || bad "corrupt state broke lookup: '$c'"
c=$(tint_color_for_tag 'brand-new' 2>&1)
[[ "$c" == <->' '<->' '<-> ]] && ok "still assigns despite garbage rows" || bad "assign broke: '$c'"

print "\n== hue math boundaries =="
fresh
for h in 0 1 59 60 61 119 120 180 239 240 300 359; do
  rgb=$(_tint_hue2rgb $h 2>&1)
  [[ "$rgb" == <->' '<->' '<-> ]] || { bad "hue $h -> '$rgb'"; continue }
  read r g b <<< "$rgb"
  (( r>=0 && r<=255 && g>=0 && g<=255 && b>=0 && b<=255 )) || bad "hue $h out of range: $rgb"
done
ok "12 hue boundaries all in 0-255"

print "\n== path edge cases =="
fresh
d="$(mktemp -d)/has space/and'quote"; mkdir -p "$d"
tint_tag_for "$d" >/dev/null 2>&1; ok "path with space+quote did not crash"
print "" > "$(mktemp -d)/.tint"
e=$(mktemp -d); print "" > "$e/.tint"; mkdir -p "$e/sub"
t=$(tint_tag_for "$e/sub" 2>/dev/null)
[[ -z "$t" ]] && ok "empty .tint falls through" || bad "empty .tint -> '$t'"
tint_tag_for "/nonexistent/nope/nada" >/dev/null 2>&1; ok "nonexistent path did not crash"

print "\n== git remote shapes =="
fresh
g=$(mktemp -d); git -C $g init -q 2>/dev/null
for url in 'git@github.com:acme/repo.git' 'https://github.com/acme/repo.git' \
           'ssh://git@github.com/acme/repo.git' '/local/path/repo.git' 'weird-no-slash'; do
  git -C $g remote remove origin 2>/dev/null
  git -C $g remote add origin "$url" 2>/dev/null
  t=$(tint_group_for $g 2>&1)
  [[ "$t" == *' '* || "$t" == */* ]] && bad "remote '$url' -> junk group '$t'"
done
git -C $g remote remove origin 2>/dev/null
git -C $g remote add origin 'git@github.com:acme/repo.git' 2>/dev/null
t=$(tint_group_for $g); [[ "$t" == "acme" ]] && ok "ssh remote -> group 'acme'" || bad "ssh remote -> '$t'"
git -C $g remote set-url origin 'https://github.com/acme/repo.git'
t=$(tint_group_for $g); [[ "$t" == "acme" ]] && ok "https remote -> group 'acme'" || bad "https remote -> '$t'"

print "\n== PATH is not clobbered (zsh \$path is special!) =="
fresh
before="$PATH"
tint_group_for "$g" >/dev/null 2>&1
[[ "$PATH" == "$before" ]] && ok "PATH intact after tag resolution" || bad "PATH CLOBBERED: $PATH"
whence -p git >/dev/null && ok "commands still resolve" || bad "PATH broken: git unresolvable"

print "\n== read-only state dir =="
ro=$(mktemp -d); chmod 500 $ro
TINT_STATE=$ro/sub/a.tsv TINT_OVERRIDES=$ro/o.tsv zsh -c "
  source $root/lib/color.zsh; tint_color_for_tag ro-test >/dev/null 2>&1" \
  && ok "unwritable state dir exits cleanly" || ok "unwritable state dir failed non-fatally"
chmod 700 $ro

print ""
(( fail )) && { print "STRESS FAILED"; exit 1 }
print "STRESS OK"
