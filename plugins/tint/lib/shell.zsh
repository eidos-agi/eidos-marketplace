# tint for plain (non-Claude) shells: recolour on cd.
# Claude Code sessions are handled by hooks/tint-hook.sh instead, because chpwd
# never fires while claude owns the terminal.
source ${0:A:h}/color.zsh
source ${0:A:h}/tag.zsh
path=($path ${0:A:h:h}/bin)

# ponytail: tint_apply, NOT tint_emit. Emitting escapes straight to the tty is
# dead inside tmux (allow-passthrough is off by default and eats them), which is
# exactly where most of these shells live. apply picks tmux-vs-escapes for us.
_tint_chpwd() { local t g; t=$(tint_tag_for "$PWD"); g=$(tint_group_for "$PWD"); tint_apply "$t" "$g" /dev/tty }
autoload -Uz add-zsh-hook
add-zsh-hook chpwd _tint_chpwd
_tint_chpwd
