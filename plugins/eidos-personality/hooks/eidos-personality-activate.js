#!/usr/bin/env node
// eidos-personality — Claude Code SessionStart activation hook.
//
// Runs on every session start / resume / clear / compact. It reads the
// plain-speech skill, strips the frontmatter, and writes it to stdout. Claude
// Code takes a SessionStart hook's stdout and injects it into the session as
// standing context, so the personality is in front of the model for every
// reply. This is the same mechanism ponytail uses.
//
// The personality is ON by default. It turns off only when the state file says
// "off" or EIDOS_PERSONALITY=off is set.

const fs = require('fs');
const path = require('path');
const os = require('os');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const statePath = path.join(claudeDir, '.eidos-personality-active');
const skillPath = path.join(__dirname, '..', 'skills', 'eidos-personality', 'SKILL.md');

function getState() {
  // Env var wins. Then the state file. Default is on.
  const env = (process.env.EIDOS_PERSONALITY || '').trim().toLowerCase();
  if (env === 'off') return 'off';
  if (env === 'on') return 'on';
  try {
    const v = fs.readFileSync(statePath, 'utf8').trim().toLowerCase();
    if (v === 'off') return 'off';
  } catch (e) {
    // No state file yet — that is the default-on case.
  }
  return 'on';
}

function skillBody() {
  // Read the skill and drop the YAML frontmatter block at the top.
  const raw = fs.readFileSync(skillPath, 'utf8');
  return raw.replace(/^---[\s\S]*?---\s*/, '');
}

const HEADER = 'EIDOS PERSONALITY ACTIVE — trait: plain speech\n\n';

const FALLBACK =
  HEADER +
  'How you talk now, on every reply. You understand more than you should say;' +
  ' hand the reader the plain version.\n' +
  '1. Lead with what happened, not how big it is.\n' +
  '2. Say the plain words for a coined term before you use the term.\n' +
  '3. Plain explanation first; a metaphor only after it, never instead.\n' +
  '4. Short sentences. Do not stack clauses.\n' +
  '5. End with one clear ask, not a menu (unless options were requested).\n' +
  '6. Translate down, do not dump. Say the version a smart person who was not' +
  ' in the room could follow.\n' +
  'Plain is not vague: say the true thing in simple words, and never drop a' +
  ' caveat to sound cleaner.\n' +
  'Off only on "stop eidos-personality" / "normal voice".';

if (getState() === 'off') {
  // Say nothing — no context injected.
  process.exit(0);
}

let output;
try {
  output = HEADER + skillBody();
} catch (e) {
  output = FALLBACK;
}

process.stdout.write(output);
