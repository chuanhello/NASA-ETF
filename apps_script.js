/**
 * Google Apps Script for NASA ETF & SpaceX SPV Tracker
 * Paste this script into your Google Sheet: Extensions > Apps Script
 * Deploy it as a Web App: 
 *   - Click "Deploy" > "New deployment"
 *   - Select type: "Web app"
 *   - Execute as: "Me" (your Google account)
 *   - Who has access: "Anyone"
 *   - Copy the Web App URL and set it as a GitHub Repository Secret named GOOGLE_SHEET_WEBAPP_URL
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var date = data.date;
    var top10 = data.top10; // Array of {rank, ticker, name, weight, shares}
    var spacexSpvShares = data.spacex_spv_shares;
    var spacexCommonShares = data.spacex_common_shares;

    var ss = SpreadsheetApp.getActiveSpreadsheet();

    // 1. Process SpaceX Shares Sheet
    var spacexSheet = getOrCreateSheet(ss, "SpaceX_SPV_Shares");
    updateSpaceXShares(spacexSheet, date, spacexSpvShares, spacexCommonShares);

    // 2. Process NASA Top 10 Sheet
    var top10Sheet = getOrCreateSheet(ss, "NASA_Top_10_Holdings");
    updateTop10Holdings(top10Sheet, date, top10);

    return ContentService.createTextOutput(JSON.stringify({ status: "success", message: "Data synced successfully for " + date }))
                         .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}

function updateSpaceXShares(sheet, date, spvShares, commonShares) {
  var headers = ["Date", "SpaceX SPV Shares (from ETF CSV)", "SpaceX Common Share Equivalents (from Web)"];
  
  // Set headers if empty
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.getRange("A1:C1").setFontWeight("bold").setBackground("#f3f3f3").setHorizontalAlignment("center");
  }

  // Check if date already exists to prevent duplicate entries
  var lastRow = sheet.getLastRow();
  var dateExists = false;
  if (lastRow > 1) {
    var dates = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
    for (var i = 0; i < dates.length; i++) {
      var d = dates[i][0];
      if (formatDate(d) === formatDate(date)) {
        dateExists = true;
        // Update existing row
        sheet.getRange(i + 2, 2).setValue(spvShares);
        sheet.getRange(i + 2, 3).setValue(commonShares);
        break;
      }
    }
  }

  if (!dateExists) {
    sheet.appendRow([date, spvShares, commonShares]);
  }

  // Formatting
  sheet.getRange("A2:A" + sheet.getLastRow()).setHorizontalAlignment("center");
  sheet.getRange("B2:C" + sheet.getLastRow()).setNumberFormat("#,##0.00").setHorizontalAlignment("right");
  sheet.autoResizeColumns(1, 3);
}

function updateTop10Holdings(sheet, date, top10) {
  var headers = ["Date", "Rank", "Ticker", "Company Name", "Weight (%)", "Shares"];
  
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.getRange("A1:F1").setFontWeight("bold").setBackground("#f3f3f3").setHorizontalAlignment("center");
  }

  var lastRow = sheet.getLastRow();
  
  // Remove existing entries for this date if they exist (to overwrite/update)
  if (lastRow > 1) {
    var dates = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
    // Loop backwards to safely delete multiple rows
    for (var i = dates.length - 1; i >= 0; i--) {
      var d = dates[i][0];
      if (formatDate(d) === formatDate(date)) {
        sheet.deleteRow(i + 2);
      }
    }
  }

  // Append new top 10
  for (var k = 0; k < top10.length; k++) {
    var item = top10[k];
    sheet.appendRow([
      date,
      item.rank,
      item.ticker,
      item.name,
      item.weight / 100, // Format as decimal so Google Sheets can format as percentage
      item.shares
    ]);
  }

  // Formatting
  var newLastRow = sheet.getLastRow();
  sheet.getRange("A2:C" + newLastRow).setHorizontalAlignment("center");
  sheet.getRange("D2:D" + newLastRow).setHorizontalAlignment("left");
  sheet.getRange("E2:E" + newLastRow).setNumberFormat("0.00%").setHorizontalAlignment("right");
  sheet.getRange("F2:F" + newLastRow).setNumberFormat("#,##0.00").setHorizontalAlignment("right");
  sheet.autoResizeColumns(1, 6);
}

function formatDate(dateObjOrStr) {
  if (dateObjOrStr instanceof Date) {
    var year = dateObjOrStr.getFullYear();
    var month = ("0" + (dateObjOrStr.getMonth() + 1)).slice(-2);
    var day = ("0" + dateObjOrStr.getDate()).slice(-2);
    return year + "-" + month + "-" + day;
  }
  if (typeof dateObjOrStr === "string") {
    return dateObjOrStr.split("T")[0]; // handle ISO strings
  }
  return dateObjOrStr;
}
