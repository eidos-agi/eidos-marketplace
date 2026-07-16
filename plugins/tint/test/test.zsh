#!/bin/zsh
# The smallest thing that fails if tint breaks:  zsh test/test.zsh
# Runs against a temp state dir so it never touches your real assignments.
emulate -L zsh
setopt err_return

root=${0:A:h:h}
export TINT_STATE=$(mktemp -d)/assigned.tsv
export TINT_OVERRIDES=${TINT_STATE:h}/overrides.tsv
source $root/lib/color.zsh
source $root/lib/tag.zsh

fail=0
ok()  { print -r -- "  ok  $1" }
bad() { print -r -- "  FAIL $1"; fail=1 }
is()  { [[ "$2" == "$3" ]] && ok "$1" || bad "$1: got '$2' want '$3'" }

print "tag extraction -- NAME is the repo, GROUP is the org (they differ on purpose)"
is "name = repo"      "$(tint_tag_for $HOME/repos-eidos-agi/tint)"    "tint"
is "group = org"      "$(tint_group_for $HOME/repos-eidos-agi/tint)"  "eidos-agi"
is "name nested"      "$(tint_tag_for $HOME/repos-greenmark/a/b/c)"   "a"
is "group nested"     "$(tint_group_for $HOME/repos-greenmark/a/b/c)" "greenmark"
# The bug this split exists to kill: 211 of 664 real projects shared one org, so
# colouring AND naming by org made 211 windows identical. Sibling repos must not
# collide by name, but SHOULD share a colour.
is "sibling name A"   "$(tint_tag_for $HOME/repos-eidos-agi/helios)"  "helios"
is "sibling name B"   "$(tint_tag_for $HOME/repos-eidos-agi/kai)"     "kai"
is "siblings share a colour" "$(tint_group_for $HOME/repos-eidos-agi/helios)" "$(tint_group_for $HOME/repos-eidos-agi/kai)"
tint_tag_for /etc/passwd >/dev/null 2>&1 && bad "untagged path should fail" || ok "untagged path -> no tag"

print "\n.tint file overrides the guess"
d=$(mktemp -d)/proj/sub; mkdir -p $d; print "billing project" > ${d:h}/.tint
is ".tint wins + spaces->dashes" "$(tint_tag_for $d)" "billing-project"
print "  (.tint sets the NAME; .tint-group would set the colour bucket)"

print "\nSTABILITY -- the property the whole design exists to protect"
a=$(tint_color_for_tag alpha)
b=$(tint_color_for_tag beta)
for t in gamma delta epsilon zeta; do tint_color_for_tag $t >/dev/null; done
is "alpha unchanged after 4 new tags" "$(tint_color_for_tag alpha)" "$a"
is "beta unchanged after 4 new tags"  "$(tint_color_for_tag beta)"  "$b"
is "repeat call is identical"         "$(tint_color_for_tag alpha)" "$a"

print "\nDISTINCTNESS -- the bug that killed the hash-into-a-wheel version"
# jetta/aic landed on the same blue when hashing. Assignment must not do that.
typeset -a hues=( ${(f)"$(cut -f2 $TINT_STATE)"} )
min=360
for (( i=1; i<=${#hues}; i++ )); do
  for (( j=i+1; j<=${#hues}; j++ )); do
    d=$(( (hues[i] - hues[j]) % 360 )); (( d < 0 )) && d=$(( d + 360 ))
    (( d > 180 )) && d=$(( 360 - d ))
    (( d < min )) && min=$d
  done
done
(( min >= 45 )) && ok "6 tags, min hue gap ${min}deg (>=45)" || bad "hues too close: ${min}deg"

print "\noverrides"
printf 'muted\tnone\n' > $TINT_OVERRIDES
printf 'brand\t10 20 30\n' >> $TINT_OVERRIDES
is "explicit rgb" "$(tint_color_for_tag brand)" "10 20 30"
is "'none' suppresses (not the '-' that zsh echo eats)" "$(tint_color_for_tag muted)" ""

print "\ncolor math"
is "hue 0 is red-ish"  "$(_tint_hue2rgb 0)"   "225 71 71"
is "hue 120 is green"  "$(_tint_hue2rgb 120)" "71 225 71"
is "hue 240 is blue"   "$(_tint_hue2rgb 240)" "71 71 225"
is "bg tint is dimmed" "$(TINT_DIM=13 tint_bgtint_for_tag brand)" "#010203"

print ""
(( fail )) && { print "FAILED"; exit 1 }
print "OK"
