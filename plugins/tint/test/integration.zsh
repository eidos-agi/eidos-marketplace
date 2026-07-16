#!/bin/zsh
# The hook and the CLI -- i.e. the parts users actually touch.
#   zsh test/integration.zsh
emulate -L zsh

root=${0:A:h:h}
fail=0
ok()  { print -r -- "  ok   $1" }
bad() { print -r -- "  FAIL $1"; fail=1 }

export TINT_STATE=$(mktemp -d)/assigned.tsv
export TINT_OVERRIDES=${TINT_STATE:h}/overrides.tsv

print "== hook: must never hang, never emit to stdout, always exit 0 =="
# A hook that blocks on stdin would freeze every Claude turn forever.
proj=$(mktemp -d)/repos-acme/thing; mkdir -p $proj
print "acme" > ${proj:h}/.tint   # fixture must actually be taggable, or we test nothing
out=$(CLAUDE_PROJECT_DIR=$proj timeout 5 zsh $root/hooks/tint-hook.sh < /dev/null 2>&1)
rc=$?
(( rc == 124 )) && bad "HOOK HANGS with no stdin (timeout)" || ok "no stdin -> returns"
(( rc == 0 )) || bad "exit code $rc (must be 0 or Claude surfaces an error)"
[[ -z "$out" ]] && ok "silent on stdout/stderr" || bad "hook printed: '$out'"

out=$(printf '' | CLAUDE_PROJECT_DIR=$proj timeout 5 zsh $root/hooks/tint-hook.sh 2>&1); rc=$?
(( rc == 124 )) && bad "HOOK HANGS on empty stdin" || ok "empty stdin -> returns"

out=$(printf 'not json at all' | CLAUDE_PROJECT_DIR=$proj timeout 5 zsh $root/hooks/tint-hook.sh 2>&1); rc=$?
[[ $rc -eq 0 && -z "$out" ]] && ok "garbage stdin -> silent, exit 0" || bad "garbage stdin: rc=$rc out='$out'"

print "\n== hook: PostToolUse payload parsing =="
payload='{"tool_name":"Edit","tool_input":{"file_path":"/tmp/x/repos-zeta/a.py","old_string":"a"}}'
extract() {  # mirror the hook's extraction so we can assert on it
  local p=$1 t=""
  [[ "$p" =~ '"file_path"[[:space:]]*:[[:space:]]*"([^"]*)"' ]] && t=$match[1]
  print -r -- "$t"
}
[[ "$(extract $payload)" == "/tmp/x/repos-zeta/a.py" ]] && ok "extracts file_path" || bad "extract -> '$(extract $payload)'"
[[ -z "$(extract '{"tool_input":{}}')" ]] && ok "absent file_path -> empty" || bad "absent file_path leaked"
[[ -z "$(extract 'garbage')" ]] && ok "garbage -> empty" || bad "garbage leaked"
p2='{"tool_input":{"file_path":"/a/b c/d.py"}}'
[[ "$(extract $p2)" == "/a/b c/d.py" ]] && ok "path with space" || bad "space path -> '$(extract $p2)'"

print "\n== hook: emits the real bytes, end to end =="
# script(1) captures nothing on macOS -- even a raw printf -- so it cannot test
# this. TINT_TTY injects the target instead, which tests the whole chain minus
# the ps-walk (covered separately below).
sink=$(mktemp)
TINT_TTY=$sink CLAUDE_PROJECT_DIR=$proj timeout 5 zsh $root/hooks/tint-hook.sh < /dev/null
grep -q $'\033]11;#' $sink && ok "OSC 11 (window bg) emitted" || bad "no OSC 11 in output"
grep -q $'\033]6;1;bg;red' $sink && ok "OSC 6 (tab colour) emitted" || bad "no OSC 6 in output"

# PostToolUse must follow the EDITED FILE, not cwd -- the whole cross-repo claim.
other=$(mktemp -d)/repos-omega/x; mkdir -p $other; print "omega" > ${other:h}/.tint
sink2=$(mktemp)
print -r -- "{\"tool_input\":{\"file_path\":\"$other/f.py\"}}" \
  | TINT_TTY=$sink2 CLAUDE_PROJECT_DIR=$proj timeout 5 zsh $root/hooks/tint-hook.sh
acme_rgb=$(zsh -c "source $root/lib/color.zsh; tint_color_for_tag acme")
omega_rgb=$(zsh -c "source $root/lib/color.zsh; tint_color_for_tag omega")
r=${omega_rgb%% *}
if grep -q "bg;red;brightness;$r" $sink2 && [[ "$acme_rgb" != "$omega_rgb" ]]; then
  ok "PostToolUse followed the edited file (omega), not cwd (acme)"
else
  bad "PostToolUse used cwd instead of the edited file"
fi

# An untaggable target must leave the window ALONE, not reset it to default.
sink3=$(mktemp)
TINT_TTY=$sink3 CLAUDE_PROJECT_DIR=/etc timeout 5 zsh $root/hooks/tint-hook.sh < /dev/null
[[ ! -s $sink3 ]] && ok "untaggable dir -> emits nothing (window untouched)" \
                  || bad "untaggable dir wrote: $(od -c $sink3 | head -1)"

print "\n== tmux: a REAL session (escapes never reach the emulator there) =="
if command -v tmux >/dev/null 2>&1; then
  ts=tint-test-$$
  tmux new-session -d -s $ts -x 80 -y 24 2>/dev/null
  tmux send-keys -t $ts "cd $proj && TINT_STATE=$TINT_STATE TINT_OVERRIDES=$TINT_OVERRIDES CLAUDE_PROJECT_DIR=$proj zsh $root/hooks/tint-hook.sh </dev/null; tmux wait -S tdone" Enter
  tmux wait tdone 2>/dev/null
  nm=$(tmux display -p -t $ts '#{window_name}' 2>/dev/null)
  st=$(tmux show -p -t $ts window-style 2>/dev/null)
  ar=$(tmux show -w -t $ts -v automatic-rename 2>/dev/null)
  want=$(zsh -c "source $root/lib/color.zsh; TINT_STATE=$TINT_STATE tint_bgtint_for_tag acme")
  [[ "$nm" == "acme" ]] && ok "tmux window renamed to the tag (NAME IS THE GAME)" || bad "tmux name -> '$nm'"
  [[ "$st" == *"bg=$want"* ]] && ok "tmux pane bg = $want" || bad "tmux bg -> '$st' want '$want'"
  [[ "$ar" == "off" ]] && ok "automatic-rename disabled (else tmux overwrites the name)" || bad "automatic-rename=$ar"
  tmux kill-session -t $ts 2>/dev/null
else
  ok "skipped (no tmux)"
fi

print "\n== plain shell in tmux: the DOCUMENTED install, and it was dead =="
if command -v tmux >/dev/null 2>&1; then
  ss=tint-sh-$$
  tmux new-session -d -s $ss -x 80 -y 24 2>/dev/null
  tmux send-keys -t $ss "export TINT_STATE=$TINT_STATE TINT_OVERRIDES=$TINT_OVERRIDES; source $root/lib/shell.zsh; cd $proj; tmux wait -S s1" Enter
  tmux wait s1 2>/dev/null
  [[ "$(tmux display -p -t $ss '#{window_name}')" == "acme" ]] \
    && ok "cd into a topic renames the tmux window" || bad "shell.zsh dead in tmux (name=$(tmux display -p -t $ss '#{window_name}'))"
  tmux show -p -t $ss window-style 2>/dev/null | grep -q 'bg=#' \
    && ok "cd into a topic sets the pane bg" || bad "shell.zsh set no bg in tmux"
  # A STALE name is worse than no name -- tmux never re-renames on its own.
  tmux send-keys -t $ss "cd /etc; tmux wait -S s2" Enter; tmux wait s2 2>/dev/null
  [[ "$(tmux display -p -t $ss '#{window_name}')" != "acme" ]] \
    && ok "cd out clears the name (no stale topic)" || bad "STALE NAME: still 'acme' outside the topic"
  tmux send-keys -t $ss "cd $proj; tmux wait -S s3" Enter; tmux wait s3 2>/dev/null
  [[ "$(tmux display -p -t $ss '#{window_name}')" == "acme" ]] \
    && ok "cd back in restores the name (round-trips)" || bad "name did not come back"
  tmux kill-session -t $ss 2>/dev/null
else
  ok "skipped (no tmux)"
fi

print "\n== the ps-walk finds a real tty (this process has one upstream) =="
found=$(zsh -c '
  _f() { local p=$$ t; while [[ -n "$p" && "$p" -gt 1 ]]; do
    t=$(ps -o tty= -p "$p" 2>/dev/null | tr -d " ")
    [[ -n "$t" && "$t" != "??" ]] && { echo "/dev/$t"; return 0 }
    p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d " "); done; return 1 }
  _f')
if [[ "$found" == /dev/tty* && -c "$found" ]]; then
  ok "walk resolved a real character device: $found"
elif [[ -z "$found" ]]; then
  ok "no tty upstream (headless runner) -- hook correctly no-ops"
else
  bad "walk returned a non-tty: '$found'"
fi

print "\n== stale lock must not wedge every future call =="
mkdir -p ${TINT_STATE:h}; : > $TINT_STATE
mkdir "${TINT_STATE}.lock"          # simulate a crashed holder
start=$SECONDS
zsh -c "source $root/lib/color.zsh; tint_color_for_tag stale-test >/dev/null 2>&1"
took=$(( SECONDS - start ))
(( took < 3 )) && ok "stale lock cleared/bypassed in ${took}s" || bad "stale lock cost ${took}s per call"
rmdir "${TINT_STATE}.lock" 2>/dev/null

print "\n== corrupt hue values must not emit garbage =="
export TINT_STATE=$(mktemp -d)/s.tsv
printf 'badhue\tnotanumber\nneg\t-5\nhuge\t99999\n' > $TINT_STATE
source $root/lib/color.zsh
for t in badhue neg huge; do
  rgb=$(tint_color_for_tag $t 2>&1)
  if [[ "$rgb" == <->' '<->' '<-> ]]; then
    read r g b <<< "$rgb"
    (( r>=0 && r<=255 && g>=0 && g<=255 && b>=0 && b<=255 )) \
      || bad "tag '$t' -> out-of-range rgb '$rgb'"
  else
    bad "tag '$t' -> non-rgb '$rgb'"
  fi
done
ok "corrupt hues produce valid in-range rgb"

print "\n== CRLF state file (edited on another machine) =="
export TINT_STATE=$(mktemp -d)/s.tsv
printf 'crlf\t90\r\n' > $TINT_STATE
source $root/lib/color.zsh
rgb=$(tint_color_for_tag crlf 2>&1)
[[ "$rgb" == <->' '<->' '<-> ]] && ok "CRLF row parsed" || bad "CRLF row -> '$rgb'"

print "\n== .tint hygiene =="
export TINT_STATE=$(mktemp -d)/s.tsv
source $root/lib/color.zsh; source $root/lib/tag.zsh
d=$(mktemp -d); print "  spaced topic  " > $d/.tint
t=$(tint_tag_for $d)
[[ "$t" != -* && "$t" != *- ]] && ok "leading/trailing space -> clean tag '$t'" \
                              || bad ".tint whitespace -> dashes at edges: '$t'"

print "\n== CLI =="
export TINT_STATE=$(mktemp -d)/s.tsv
export TINT_OVERRIDES=${TINT_STATE:h}/o.tsv
o=$(cd $(mktemp -d) && zsh $root/bin/tint 2>&1); rc=$?
(( rc == 0 )) && ok "status in untagged dir exits 0" || bad "status untagged: rc=$rc '$o'"
o=$(zsh $root/bin/tint list 2>&1); rc=$?
(( rc == 0 )) && ok "list on empty state exits 0" || bad "list empty: rc=$rc '$o'"
o=$(zsh $root/bin/tint --help 2>&1)
[[ "$o" == *"tint"*"topic"* ]] && ok "--help shows usage" || bad "--help broken: '$o'"
o=$(cd $(mktemp -d) && zsh $root/bin/tint off 2>&1); rc=$?
(( rc != 0 )) && ok "off in untagged dir fails cleanly" || bad "off untagged should fail: '$o'"
w=$(mktemp -d); o=$(cd $w && zsh $root/bin/tint 'my topic' 2>&1)
[[ -f $w/.tint ]] && ok "tint <topic> wrote .tint" || bad "no .tint written"
t=$(cd $w && zsh -c "source $root/lib/tag.zsh; tint_tag_for \$PWD")
[[ "$t" == "my-topic" ]] && ok "pinned topic round-trips as 'my-topic'" || bad "pin round-trip -> '$t'"

print "\n== sourcing shell.zsh must be SILENT (no controlling terminal) =="
# /dev/tty is crw-rw-rw- so [[ -w ]] lies; the OPEN fails and the error escapes
# 2>/dev/null. This spammed every non-interactive shell that sourced tint.
noise=$(zsh -c "source $root/lib/shell.zsh; cd /tmp" 2>&1)
[[ -z "$noise" ]] && ok "non-interactive source is silent" || bad "startup noise: '$noise'"

print "\n== shell.zsh sources cleanly and does not wreck PATH =="
before=$PATH
o=$(zsh -c "source $root/lib/shell.zsh 2>&1; print -r -- \"PATHOK=\$([[ -n \$PATH ]] && echo yes)\"; whence -p git >/dev/null && echo GITOK")
[[ "$o" == *PATHOK=yes* ]] && ok "PATH non-empty after source" || bad "shell.zsh wrecked PATH: '$o'"
[[ "$o" == *GITOK* ]] && ok "commands resolve after source" || bad "shell.zsh broke command lookup"
[[ "$o" != *"not found"* && "$o" != *error* ]] && ok "sources without error" || bad "source errors: '$o'"

print ""
(( fail )) && { print "INTEGRATION FAILED"; exit 1 }
print "INTEGRATION OK"
