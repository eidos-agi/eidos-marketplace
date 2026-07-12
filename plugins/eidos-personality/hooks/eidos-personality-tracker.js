#!/usr/bin/env node
// eidos-personality — UserPromptSubmit hook.
//
// Watches what the user types for a request to turn the personality off or
// back on, and writes the choice to the state file so it sticks across the
// session. It also re-injects the reminder when the user turns it back on
// mid-session, so the model does not have to wait for the next SessionStart.

const fs = require('fs');
const path = require('path');
const os = require('os');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const statePath = path.join(claudeDir, '.eidos-personality-active');

function setState(value) {
  try {
    fs.mkdirSync(path.dirname(statePath), { recursive: true });
    fs.writeFileSync(statePath, value);
  } catch (e) {
    // Best-effort — never block the prompt over a state write.
  }
}

let input = '';
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input.replace(/^﻿/, ''));
    const prompt = (data.prompt || '').trim().toLowerCase();

    // Turn off.
    if (/\b(stop eidos-personality|normal voice)\b/.test(prompt)) {
      setState('off');
      process.stdout.write('EIDOS PERSONALITY OFF');
      return;
    }

    // Turn back on.
    if (/\b(start eidos-personality|plain speech on|eidos voice on)\b/.test(prompt)) {
      setState('on');
      process.stdout.write(
        'EIDOS PERSONALITY ON — trait: plain speech. Lead with the fact,' +
        ' define shorthand before use, plain before metaphor, short sentences,' +
        ' one ask, translate down. Plain is not vague — keep every caveat.'
      );
      return;
    }
  } catch (e) {
    // Silent fail — never block the prompt.
  }
});
