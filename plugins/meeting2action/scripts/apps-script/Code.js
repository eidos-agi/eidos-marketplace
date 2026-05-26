const SOURCE_FOLDER_NAME = "Meet Recordings";
const DEST_FOLDER_ID = "__EIDOS_FOUNDERS_RECORDINGS_FOLDER_ID__";
const MAX_AGE_HOURS = 72;
const TRIGGER_MINUTES = 15;

function syncMeetRecordings() {
  const props = PropertiesService.getScriptProperties();
  if (!DEST_FOLDER_ID || DEST_FOLDER_ID.includes("__EIDOS_")) {
    throw new Error("Missing DEST_FOLDER_ID. Install with the Eidos destination folder ID.");
  }

  const sourceFolders = DriveApp.getFoldersByName(SOURCE_FOLDER_NAME);
  if (!sourceFolders.hasNext()) {
    throw new Error(`Source folder not found: ${SOURCE_FOLDER_NAME}`);
  }

  const source = sourceFolders.next();
  const dest = DriveApp.getFolderById(DEST_FOLDER_ID);
  const files = source.getFiles();

  while (files.hasNext()) {
    const file = files.next();
    const id = file.getId();
    if (props.getProperty(processedKey_(id))) continue;

    const created = file.getDateCreated();
    const ageHours = (Date.now() - created.getTime()) / 36e5;
    if (ageHours > MAX_AGE_HOURS) continue;

    const name = file.getName();
    if (!isLikelyFounderMeetArtifact_(name)) continue;

    const copy = file.makeCopy(name, dest);
    props.setProperty(
      processedKey_(id),
      JSON.stringify({
        copiedAt: new Date().toISOString(),
        sourceId: id,
        copyId: copy.getId(),
        name: name,
      })
    );
  }
}

function installTimeTrigger() {
  deleteRouterTriggers_();
  ScriptApp.newTrigger("syncMeetRecordings")
    .timeBased()
    .everyMinutes(TRIGGER_MINUTES)
    .create();
}

function deleteRouterTriggers_() {
  ScriptApp.getProjectTriggers().forEach((trigger) => {
    if (trigger.getHandlerFunction() === "syncMeetRecordings") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function isLikelyFounderMeetArtifact_(name) {
  const lower = name.toLowerCase();
  return (
    lower.includes("founder") ||
    lower.includes("daniel") ||
    lower.includes("vybhav") ||
    lower.includes("meet") ||
    lower.includes("recording") ||
    lower.includes("transcript")
  );
}

function processedKey_(fileId) {
  return `processed:${fileId}`;
}
