function MyScrollBar2() {
    $('a[data-toggle="tab"]').on("shown.bs.tab", function(e) {
        var targetTab = $(e.target).attr("href");
        var api;
        var throttleTimeout = null;
        log_array.forEach(function(log) {
            if (targetTab === "#" + log.id_tab) {
                $("#" + log.name + "_values").jScrollPane();
                api = $("#" + log.name + "_values").data("jsp");
                reinitScroll(api, throttleTimeout)
            }
        })
    });
    $(".table-scroll-horizontal").on("jsp-scroll-x", function(event, scrollPositionX, isAtLeft, isAtRight) {
        $(this).find(".headcol").css({
            transform: "translateX(" + scrollPositionX + "px)"
        })
    })
}
function fillSecTab(blobsarray, log, $tab) {
    if (blobsarray != undefined) {
        for (var $j = 0, len = $secLogHeader.length; $j < len; $j++) {
            for (var $i = 0; $i < blobsarray.length; $i++) {
                var $id = log.id_name + $secLogHeader[$j][0] + "_" + $i;
                if (document.getElementById($id) != null) {
                    document.getElementById($id).innerHTML = blobsarray[$i][$secLogHeader[$j][0]]
                }
            }
        }
    }
}
function createSecLogObject(parsedBlobSL, timestamp, version, versionFA100, logg, SRN) {
    var blobObject = {};
    var dividedByte1 = divideByte([6, 1], parsedBlobSL[1]);
    var dividedByte2 = divideByte([5, 1, 1], parsedBlobSL[2]);
    var dividedByte3 = divideByte([5, 1, 1], parsedBlobSL[3]);
    var dividedByte4 = divideByte([5, 1, 1], parsedBlobSL[4]);
    var dividedByte5 = divideByte([5, 1, 1], parsedBlobSL[5]);
    var dividedByte6 = divideByte([5, 1, 1], parsedBlobSL[6]);
    var dividedByte7 = divideByte([5, 1, 1], parsedBlobSL[7]);
    var dividedByte8 = divideByte([5, 1, 1], parsedBlobSL[8]);
    var dividedByte9 = divideByte([5, 2, 1], parsedBlobSL[9]);
    var dividedByte10 = divideByte([5, 2, 1], parsedBlobSL[10]);
    var dividedByte11 = divideByte([5, 2, 1], parsedBlobSL[11]);
    var dividedByte12 = divideByte([5, 2, 1], parsedBlobSL[12]);
    var dividedByte13 = divideByte([5, 2, 1], parsedBlobSL[13]);
    var dividedByte14 = divideByte([5, 2, 1], parsedBlobSL[14]);
    var dividedByte15 = divideByte([5, 2, 1], parsedBlobSL[15]);
    var dividedByte16 = divideByte([5, 2, 1], parsedBlobSL[16]);
    var dividedByte17 = divideByte([5, 2, 1], parsedBlobSL[17]);
    var dividedByte34 = divideByte([4, 3], parsedBlobSL[34]);
    var dividedByte36 = divideByte([3, 3, 1], parsedBlobSL[36]);
    var uErrorFileNr = dividedByte1[0];
    var uFilterSupplyFul = dividedByte1[1];
    var uTimeSupCond = dividedByte2[0];
    var uFilterExtractFul = dividedByte2[1];
    var uJustBooted = dividedByte2[2];
    var uTimeHumInp = dividedByte3[0];
    var uHumRedModeSet = dividedByte3[1];
    var uHumRedModeClr = dividedByte3[2];
    var uComLev0 = dividedByte4[0];
    var uSenVal0High = dividedByte4[1];
    var uSenVal1High = dividedByte4[2];
    var uComLev1 = dividedByte5[0];
    var uSenVal2High = dividedByte5[1];
    var uSenVal3High = dividedByte5[2];
    var uComLev2 = dividedByte6[0];
    var uSenVal4High = dividedByte6[1];
    var uSenVal5High = dividedByte6[2];
    var uComLev3 = dividedByte7[0];
    var uSenVal6High = dividedByte7[1];
    var uErrorCodeHigh = dividedByte7[2];
    var uTimeAbsDrying = dividedByte8[0];
    var uPressureHigh = dividedByte8[1];
    var uTimeRelDrying = dividedByte9[0];
    var uEnergyExtractedSupHigh = dividedByte9[1];
    var uTimeCooling = dividedByte10[0];
    var uEnergyRecoveredSupHigh = dividedByte10[1];
    var uTimeCO2Ventilation = dividedByte11[0];
    var uEnergyCooledSupHigh = dividedByte11[1];
    var uTimeSleepMode = dividedByte12[0];
    var uTimeTurboMode = dividedByte13[0];
    var uTimeAutoAlt = dividedByte14[0];
    var uTimeDefExh = dividedByte15[0];
    var uTimeMinAir = dividedByte16[0];
    var uErrorState = dividedByte17[0];
    var uWaterRemovedHigh = dividedByte34[0];
    var uMaxTimeSpan = dividedByte34[1];
    var uAirExchangedHigh = dividedByte36[0];
    var uErrorLineNrHigh = dividedByte36[1];
    var uAccCounter = parsedBlobSL[0];
    var uSenVal0Low = parsedBlobSL[18];
    var uSenVal1Low = parsedBlobSL[19];
    var uSenVal2Low = parsedBlobSL[20];
    var uSenVal3Low = parsedBlobSL[21];
    var uSenVal4Low = parsedBlobSL[22];
    var uSenVal5Low = parsedBlobSL[23];
    var uSenVal6Low = parsedBlobSL[24];
    var uErrorCodeLow = parsedBlobSL[25];
    var uPressureLow = parsedBlobSL[26];
    var uWaterRemovedLow = parsedBlobSL[27];
    var uEnergyExtractedLow = parsedBlobSL[28];
    var uEnergyExtractedHigh = parsedBlobSL[29];
    var uEnergyRecoveredLow = parsedBlobSL[30];
    var uEnergyRecoveredHigh = parsedBlobSL[31];
    var uEnergyCooledLow = parsedBlobSL[32];
    var uEnergyCooledHigh = parsedBlobSL[33];
    var uAirExchangedLow = parsedBlobSL[35];
    var uErrorLineNrLow = parsedBlobSL[37];
    var tim = timestampForSecLog(parseTimestamp(timestamp, false).toString());
    var dateAr = tim[0].split(".");
    blobObject["TIM"] = dateAr[0] + "." + dateAr[1] + "." + dateAr[2].substring(2, 4) + "<br>" + tim[1];
    blobObject["RES"] = uJustBooted[0];
    blobObject["TET"] = toSigned(lowPlusHigh(uSenVal4Low, uSenVal4High, 0), 8);
    blobObject["HET"] = lowPlusHigh(uSenVal5Low, uSenVal5High, 0);
    blobObject["TOU"] = toSigned(lowPlusHigh(uSenVal1Low, uSenVal1High, 0), 8);
    blobObject["HOU"] = lowPlusHigh(uSenVal2Low, uSenVal2High, 0);
    blobObject["CO2"] = lowPlusHigh(uSenVal6Low, uSenVal6High, 0) * 16;
    blobObject["TSU"] = toSigned(lowPlusHigh(uSenVal0Low, uSenVal0High, 0), 8);
    blobObject["TEH"] = toSigned(lowPlusHigh(uSenVal3Low, uSenVal3High, 0), 8);
    blobObject["APR"] = 700 + 2 * lowPlusHigh(uPressureLow, uPressureHigh, 0);
    blobObject["ADY"] = getAirDensity(blobObject["APR"], blobObject["TET"]);
    blobObject["AEX"] = (logg.aircoef * lowPlusHigh(uAirExchangedLow, getNumberFrBits(uAirExchangedHigh), 0)).toFixed(1);
    blobObject["SNR"] = SRN;
    blobObject["DL1"] = logg.Tcoef * getNumberFrBits(uComLev0);
    blobObject["DL2"] = logg.Tcoef * getNumberFrBits(uComLev1);
    blobObject["DL3"] = logg.Tcoef * getNumberFrBits(uComLev2);
    blobObject["DL4"] = logg.Tcoef * getNumberFrBits(uComLev3);
    blobObject["DL5"] = connectFormat(logg.DLmax - (blobObject["DL1"] + blobObject["DL2"] + blobObject["DL3"] + blobObject["DL4"]));
    blobObject["DL1"] = connectFormat(blobObject["DL1"]);
    blobObject["DL2"] = connectFormat(blobObject["DL2"]);
    blobObject["DL3"] = connectFormat(blobObject["DL3"]);
    blobObject["DL4"] = connectFormat(blobObject["DL4"]);
    blobObject["DSM"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeSleepMode));
    blobObject["DTM"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeTurboMode));
    blobObject["D1R"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeAutoAlt));
    blobObject["DDF"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeDefExh));
    blobObject["DMV"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeMinAir));
    blobObject["DWI"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeSupCond));
    blobObject["DHI"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeHumInp));
    blobObject["DRA"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeAbsDrying));
    blobObject["DRR"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeRelDrying));
    blobObject["DCO"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeCooling));
    blobObject["DC2"] = connectFormat(logg.Tcoef * getNumberFrBits(uTimeCO2Ventilation));
    blobObject["HRU"] = uHumRedModeSet[0];
    blobObject["HRN"] = uHumRedModeClr[0];
    blobObject["EXE"] = countEne(logg.enecoef, uEnergyExtractedLow, uEnergyExtractedHigh, uEnergyExtractedSupHigh);
    blobObject["REE"] = countEne(logg.enecoef, uEnergyRecoveredLow, uEnergyRecoveredHigh, uEnergyRecoveredSupHigh);
    var var1 = blobObject["AEX"] / logg.opho;
    var resHRP = blobObject["EXE"] > 0 && blobObject["REE"] > 0 ? blobObject["REE"] / blobObject["EXE"] * 100 : 0;
    var res = var1 < 51 ? var1 * .13 + 1 : var1 * .49 - 17;
    blobObject["HRP"] = resHRP.toFixed(0);
    blobObject["PCO"] = (res * logg.opho).toFixed(1);
    blobObject["COE"] = countEne(logg.enecoef, uEnergyCooledLow, uEnergyCooledHigh, uEnergyCooledSupHigh);
    if (dateAr[2] == "2020" && dateAr[1] == "05" && dateAr[0] == "03") {
        blobObject["ES"] = 0
    }
    blobObject["WAR"] = toSigned(lowPlusHigh(uWaterRemovedLow, uWaterRemovedHigh, undefined), 11);
    blobObject["WAR"] = blobObject["WAR"] * logg.watercoef;
    blobObject["ES"] = getNumberFrBits(uErrorState);
    blobObject["EFN"] = getNumberFrBits(uErrorFileNr);
    blobObject["ELN"] = lowPlusHigh(uErrorLineNrLow, uErrorLineNrHigh, 0);
    blobObject["ECO"] = lowPlusHigh(uErrorCodeLow, uErrorCodeHigh, 0);
    blobObject["FSF"] = uFilterSupplyFul[0];
    blobObject["FEF"] = uFilterExtractFul[0];
    blobObject["S21"] = parsedBlobSL[38];
    blobObject["S22"] = parsedBlobSL[39];
    blobObject["S23"] = parsedBlobSL[40];
    blobObject["S24"] = parsedBlobSL[41];
    blobObject["S25"] = parsedBlobSL[42];
    blobObject["S26"] = parsedBlobSL[43];
    blobObject["S27"] = parsedBlobSL[44];
    blobObject["S28"] = parsedBlobSL[45];
    blobObject["S29"] = parsedBlobSL[46];
    blobObject["S30"] = parsedBlobSL[47];
    return blobObject
}
function connectFormat(value) {
    return value == 0 ? "-" : value.toString().concat(":00")
}
function countEne(coef, uLow, uHigh, uSupHigh) {
    var uEne = toSigned(lowPlusHigh(uLow, uHigh, uSupHigh), 16);
    uEne = (uEne * coef / 2.79).toFixed(1);
    return uEne
}
