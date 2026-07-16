# tint: path -> (name, group). THE SEAM.
#
# TINT IS THE HINT, THE NAME IS THE GAME -- and they want different granularity.
# Measured on a real machine: 664 projects collapse to 17 orgs, 211 of them under
# one org. Colouring by org means 211 windows share a colour AND a name: useless.
# Naming by repo but colouring by repo is also wrong -- 664 hues don't exist.
#
# So they split:
#   NAME  = the repo      -> precise identity, never degrades, what you read
#   GROUP = the org       -> ~17 buckets, what the COLOUR encodes: "which company",
#                            seen peripherally without focusing
#
# Colour is good at coarse grouping and bad at identity. Text is good at identity.
# Each gets the job it's good at.
#
# Everything downstream is tag-agnostic: it takes two strings. To plug in a
# smarter tagger (clustering, an LLM, a manual sticky), override these two.

# Walk up from a path looking for a marker, so a tag applies to a whole tree.
_tint_find_up() {  # start marker -> path of marker, or fail
  local d=${1:A}
  [[ -f "$d" ]] && d=${d:h}
  while [[ "$d" != "/" && -n "$d" ]]; do
    [[ -e "$d/$2" ]] && { echo "$d/$2"; return 0 }
    d=${d:h}
  done
  return 1
}

_tint_read_marker() {  # path marker -> cleaned first line
  local f; f=$(_tint_find_up "$1" "$2") || return 1
  local v; read -r v < "$f"
  v=${v## }; v=${v%% }
  [[ -n "$v" ]] && { echo "${v// /-}"; return 0 }
  return 1
}

_tint_git_root() {
  local d=${1:A}; [[ -f "$d" ]] && d=${d:h}
  [[ -d "$d" ]] || return 1
  git -C "$d" rev-parse --show-toplevel 2>/dev/null
}

_tint_git_org() {
  local d=${1:A}; [[ -f "$d" ]] && d=${d:h}
  [[ -d "$d" ]] || return 1
  local url; url=$(git -C "$d" config --get remote.origin.url 2>/dev/null) || return 1
  [[ -z "$url" ]] && return 1
  # ponytail: NEVER name a local `path` in zsh -- it is tied to $PATH, so
  # assigning a URL to it clobbers command lookup for the rest of the function.
  local p
  if [[ "$url" == *://* ]]; then
    p=${url#*://}; p=${p#*@}; p=${p#*/}      # [proto://][user@]host/ORG/repo.git
  elif [[ "$url" == *:* ]]; then
    p=${url#*:}                               # user@host:ORG/repo.git
  else
    return 1                                  # local path remote -> no org
  fi
  local org=${p%%/*}
  [[ -n "$org" && "$org" != "$p" ]] && { echo "$org"; return 0 }
  return 1
}

# ~/repos-eidos-agi/tint/sub -> eidos-agi  (the layout you already wrote)
_tint_layout_group() {
  local rest=${${1:A}#$HOME/repos-}
  [[ "$rest" == "${1:A}" || -z "$rest" ]] && return 1
  local g=${rest%%/*}
  [[ -n "$g" ]] && { echo "$g"; return 0 }
  return 1
}

# ~/repos-eidos-agi/tint/sub -> tint  (first dir below the layout root)
_tint_layout_name() {
  local rest=${${1:A}#$HOME/repos-}
  [[ "$rest" == "${1:A}" || -z "$rest" ]] && return 1
  rest=${rest#*/}                       # drop the org segment
  local n=${rest%%/*}
  [[ -n "$n" && "$n" != "${1:A}" ]] && { echo "$n"; return 0 }
  return 1
}

# THE GAME: precise identity. .tint file > git repo name > layout leaf.
tint_tag_for() {
  local p=${1:-$PWD} root
  _tint_read_marker "$p" .tint && return 0
  root=$(_tint_git_root "$p") && [[ -n "$root" ]] && { echo "${root:t}"; return 0 }
  _tint_layout_name "$p" && return 0
  return 1
}

# THE HINT: coarse grouping for colour. .tint-group > git org > layout root.
# Falls back to the name so an ungrouped project still gets its own colour.
tint_group_for() {
  local p=${1:-$PWD}
  _tint_read_marker "$p" .tint-group && return 0
  _tint_git_org "$p" && return 0
  _tint_layout_group "$p" && return 0
  tint_tag_for "$p" && return 0
  return 1
}
