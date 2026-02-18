function mergePricesByClientId() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startRow = 2; // data starts here
  const lastRow = sheet.getLastRow();

  const clientIds = sheet.getRange(startRow, 1, lastRow - startRow + 1).getValues();

  // Columns to merge (C = 3, E = 5)
  const mergeCols = [3, 5];

  // First unmerge everything (safe rerun)
  mergeCols.forEach(col => {
    sheet.getRange(startRow, col, lastRow - startRow + 1).breakApart();
  });

  let blockStart = startRow;

  for (let i = 1; i <= clientIds.length; i++) {
    if (i === clientIds.length || clientIds[i][0] !== clientIds[i - 1][0]) {
      const blockEnd = startRow + i - 1;
      const height = blockEnd - blockStart + 1;

      if (height > 1) {
        mergeCols.forEach(col => {
          sheet.getRange(blockStart, col, height, 1).mergeVertically();
        });
      }

      blockStart = startRow + i;
    }
  }
}
