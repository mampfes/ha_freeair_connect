function getSecondRoomFlow(dip7, dip8) {
    var secRoomFlowCode = 2 * dip7 + dip8;
    var secondRoomFlow;
    switch (secRoomFlowCode) {
    case 0:
        secondRoomFlow = 0;
        break;
    case 1:
        secondRoomFlow = 30;
        break;
    case 2:
        secondRoomFlow = 60;
        break;
    case 3:
        secondRoomFlow = 100;
        break;
    default:
        throw "invalid value of second room flow";
        break
    }
    return secondRoomFlow
}
function getRoomArea(dip2, dip3, dip4) {
    var roomAreaCode = 4 * dip2 + 2 * dip3 + dip4;
    var roomArea = 0;
    switch (roomAreaCode) {
    case 0:
        roomArea = 20;
        break;
    case 1:
        roomArea = 25;
        break;
    case 2:
        roomArea = 35;
        break;
    case 3:
        roomArea = 45;
        break;
    case 4:
        roomArea = 60;
        break;
    case 5:
        roomArea = 75;
        break;
    case 6:
        roomArea = 30;
        break;
    case 7:
        roomArea = 50;
        break;
    default:
        throw "invalid value of room area";
        break
    }
    return roomArea
}
function getAbsHum(relHum, temp) {
    temp = parseFloat(temp);
    var ahPlusG10m3 = [];
    ahPlusG10m3[0] = 49;
    ahPlusG10m3[1] = 52;
    ahPlusG10m3[2] = 56;
    ahPlusG10m3[3] = 60;
    ahPlusG10m3[4] = 64;
    ahPlusG10m3[5] = 69;
    ahPlusG10m3[6] = 73;
    ahPlusG10m3[7] = 78;
    ahPlusG10m3[8] = 84;
    ahPlusG10m3[9] = 89;
    ahPlusG10m3[10] = 95;
    ahPlusG10m3[11] = 102;
    ahPlusG10m3[12] = 108;
    ahPlusG10m3[13] = 115;
    ahPlusG10m3[14] = 123;
    ahPlusG10m3[15] = 131;
    ahPlusG10m3[16] = 139;
    ahPlusG10m3[17] = 148;
    ahPlusG10m3[18] = 157;
    ahPlusG10m3[19] = 167;
    ahPlusG10m3[20] = 177;
    ahPlusG10m3[21] = 188;
    ahPlusG10m3[22] = 199;
    ahPlusG10m3[23] = 212;
    ahPlusG10m3[24] = 224;
    ahPlusG10m3[25] = 238;
    ahPlusG10m3[26] = 252;
    ahPlusG10m3[27] = 267;
    ahPlusG10m3[28] = 283;
    ahPlusG10m3[29] = 299;
    ahPlusG10m3[30] = 317;
    ahPlusG10m3[31] = 335;
    ahPlusG10m3[32] = 354;
    ahPlusG10m3[33] = 375;
    ahPlusG10m3[34] = 396;
    ahPlusG10m3[35] = 419;
    ahPlusG10m3[36] = 442;
    ahPlusG10m3[37] = 467;
    ahPlusG10m3[38] = 494;
    ahPlusG10m3[39] = 521;
    ahPlusG10m3[40] = 550;
    ahPlusG10m3[41] = 581;
    ahPlusG10m3[42] = 613;
    ahPlusG10m3[43] = 647;
    ahPlusG10m3[44] = 683;
    ahPlusG10m3[45] = 721;
    ahPlusG10m3[46] = 760;
    ahPlusG10m3[47] = 802;
    ahPlusG10m3[48] = 846;
    ahPlusG10m3[49] = 893;
    ahPlusG10m3[50] = 942;
    var ahMinusG10m3 = [];
    ahMinusG10m3[0] = 49;
    ahMinusG10m3[1] = 45;
    ahMinusG10m3[2] = 42;
    ahMinusG10m3[3] = 39;
    ahMinusG10m3[4] = 37;
    ahMinusG10m3[5] = 34;
    ahMinusG10m3[6] = 32;
    ahMinusG10m3[7] = 29;
    ahMinusG10m3[8] = 27;
    ahMinusG10m3[9] = 25;
    ahMinusG10m3[10] = 23;
    ahMinusG10m3[11] = 21;
    ahMinusG10m3[12] = 20;
    ahMinusG10m3[13] = 18;
    ahMinusG10m3[14] = 17;
    ahMinusG10m3[15] = 15;
    ahMinusG10m3[16] = 14;
    ahMinusG10m3[17] = 13;
    ahMinusG10m3[18] = 12;
    ahMinusG10m3[19] = 11;
    ahMinusG10m3[20] = 10;
    var absHum;
    if (temp >= 0) {
        if (temp > 50) {
            absHum = 1e3 / 10 * relHum / 100
        } else {
            absHum = ahPlusG10m3[temp] / 10 * relHum / 100
        }
    } else {
        temp = Math.abs(temp);
        if (temp > 20) {
            absHum = 5 / 10 * relHum / 100
        } else {
            absHum = ahMinusG10m3[temp] / 10 * relHum / 100
        }
    }
    var absHumRounded = absHum.toFixed(1);
    return absHumRounded
}
function getAirDensity(pressure, tempExtract) {
    var density = pressure * 100 / ((tempExtract + 273.15) * 287.058);
    density = (density + 0).toFixed(3);
    return density
}
function roundVal(val1) {
    return Math.round(val1)
}
function parseDIP(DIP, typ) {
    var DIPbits = byteToBits(DIP, 1);
    if (typ == 0) {
        return getRoomArea(DIPbits[6], DIPbits[5], DIPbits[4])
    } else {
        return getSecondRoomFlow(DIPbits[1], DIPbits[0])
    }
}
function checkPlausiPrimBlob(blob) {
    var bPlausible = true;
    if (blob["TempSupply"] < PLAUSI_TEMP_MIN || blob["TempSupply"] > PLAUSI_TEMP_MAX)
        bPlausible = false;
    if (blob["TempOutdoor"] < PLAUSI_TEMP_MIN || blob["TempOutdoor"] > PLAUSI_TEMP_MAX)
        bPlausible = false;
    if (blob["TempExhaust"] < PLAUSI_TEMP_MIN || blob["TempExhaust"] > PLAUSI_TEMP_MAX)
        bPlausible = false;
    if (blob["TempExtract"] < PLAUSI_TEMP_MIN || blob["TempExtract"] > PLAUSI_TEMP_MAX)
        bPlausible = false;
    if (blob["TempVirtSupExit"] < PLAUSI_TEMP_MIN || blob["TempVirtSupExit"] > PLAUSI_TEMP_MAX)
        bPlausible = false;
    if (blob["HumExtract"] < PLAUSI_HUM_MIN || blob["HumExtract"] > PLAUSI_HUM_MAX)
        bPlausible = false;
    if (blob["HumOutdoor"] < PLAUSI_HUM_MIN || blob["HumOutdoor"] > PLAUSI_HUM_MAX)
        bPlausible = false;
    if (blob["AirFlowAve"] < PLAUSI_AIR_MIN || blob["AirFlowAve"] > PLAUSI_AIR_MAX)
        bPlausible = false;
    return bPlausible
}
function toSigned(num, potenz) {
    var maxUn = 2;
    for (var i = 2; i <= potenz; i++) {
        maxUn = maxUn * 2
    }
    if (num >= maxUn / 2) {
        num = num - maxUn
    }
    return num
}
function correctVersion(versionFrBlob) {
    var indexDot = versionFrBlob.indexOf(".");
    var length = versionFrBlob.length;
    if (length - indexDot <= 2) {
        var strDoDot = versionFrBlob.substr(0, indexDot + 1);
        var strPoDot = versionFrBlob.substr(indexDot + 1);
        var versionNew = strDoDot + "0" + strPoDot;
        return versionNew
    }
}
