function correctVersion(versionFrBlob) {
    var indexDot = versionFrBlob.indexOf(".");
    var wantSubversion = false;
    var indexUnderscore = versionFrBlob.indexOf("x");
    var length = versionFrBlob.length;
    if (indexUnderscore > 0) {
        var strPoUnderscore = versionFrBlob.substr(indexUnderscore + 1);
        if (strPoUnderscore != "0")
            wantSubversion = true;
        length = indexUnderscore
    }
    var versionNew;
    if (length - indexDot <= 2 && length - indexDot >= 1) {
        var strDoDot = versionFrBlob.substr(0, indexDot + 1);
        var strPoDot = versionFrBlob.substr(indexDot + 1);
        if (wantSubversion) {
            versionNew = strDoDot + "0" + strPoDot;
            versionNew = versionNew.replace("x", "_")
        } else {
            strPoDot = strPoDot.substr(0, 1);
            versionNew = strDoDot + "0" + strPoDot
        }
        return versionNew
    } else {}
}
function fillOverview(blobsarray0) {
    document.getElementById("outdoor_temp_val").innerHTML = blobsarray0["TempOutdoor"].toFixed(1);
    document.getElementById("outdoor_hum_rel_val").innerHTML = blobsarray0["HumOutdoor"];
    document.getElementById("outdoor_hum_abs_val").innerHTML = blobsarray0["absHumOutdoor"];
    document.getElementById("exhaust_temp_val").innerHTML = blobsarray0["TempExhaust"].toFixed(1);
    document.getElementById("extract_temp_val").innerHTML = blobsarray0["TempExtract"].toFixed(1);
    document.getElementById("extract_hum_rel_val").innerHTML = blobsarray0["HumExtract"];
    document.getElementById("extract_hum_abs_val").innerHTML = blobsarray0["absHumExtract"];
    document.getElementById("extract_CO2_val").innerHTML = blobsarray0["CO2"];
    document.getElementById("air_flow_val").innerHTML = blobsarray0["AirFlow"];
    document.getElementById("supply_temp_val").innerHTML = blobsarray0["TempVirtSupExit"].toFixed(1);
    if (blobsarray0["bSumCooling"] == 0) {
        document.getElementById("heat_recovery_val").innerHTML = getHeatRecoveryPercentage(blobsarray0["TempExtract"], blobsarray0["TempOutdoor"], blobsarray0["TempVirtSupExit"], blobsarray0["AirFlow"]);
        document.getElementById("power_recovery_val").innerHTML = getPowerRecovery(blobsarray0["TempExtract"], blobsarray0["TempOutdoor"], blobsarray0["TempVirtSupExit"], blobsarray0["AirFlow"]);
        makeHeatRecoveryVisible()
    } else {
        document.getElementById("heat_recovery_p").style.display = "none";
        document.getElementById("power_recovery_p").style.visibility = "hidden";
        document.getElementById("OV_heat_recovery").style.display = "none";
        document.getElementById("OV_power_recovery").style.visibility = "hidden";
        document.getElementById("cooling_power_val").innerHTML = getCoolingPower(blobsarray0["AirFlow"], blobsarray0["TempExtract"], blobsarray0["TempVirtSupExit"]);
        document.getElementById("OV_cooling_power").style.display = "block";
        document.getElementById("cooling_power_p").style.display = "block"
    }
    traffic_lights(blobsarray0)
}
function fillDetails(blobsarray0, sernr) {
    document.getElementById("D_CL_val").innerHTML = blobsarray0["ComfortLevel"];
    document.getElementById("D_OPH_val").innerHTML = blobsarray0["operating_hours"];
    document.getElementById("D_FIH_val").innerHTML = blobsarray0["filter_hours"];
    document.getElementById("D_RA_val").innerHTML = blobsarray0["RoomArea"];
    document.getElementById("D_2A_val").innerHTML = blobsarray0["SecondRoomFlow"];
    document.getElementById("D_FSS_val").innerHTML = blobsarray0["FanSupplyRPM"];
    document.getElementById("D_FSE_val").innerHTML = blobsarray0["FanExtractRPM"];
    document.getElementById("D_SWV_val").innerHTML = correctVersion(blobsarray0["version"]);
    document.getElementById("D_CBV_val").innerHTML = blobsarray0["board_version"];
    document.getElementById("D_SNR_val").innerHTML = sernr;
    document.getElementById("timestamp").innerHTML = parseTimestamp(blobsarray0["timestamp"], true);
    setOMdetails(blobsarray0["State"], blobsarray0["ControlAuto"], blobsarray0["DefrostExhaust"], blobsarray0["HumRedMode"]);
    if (blobsarray0["bDeicing"] == 1) {
        $("#D_dei_val").attr("checked", "checked")
    }
}
function setProgramCheckbox(ControlAuto, defrostExhaust) {
    if (defrostExhaust == 1 || defrostExhaust == 2) {
        $("#D_dfr_val").attr("checked", "checked")
    }
    langs.forEach(function(lang) {
        switch (ControlAuto) {
        case 0:
        case "0":
            $("#D_mve_val").attr("checked", "checked");
            fillLangSetById("PL_PRG_val", lang.name, lang.prg_min_vent_short);
            return;
        case 1:
        case "1":
            $("#D_hrr_val").attr("checked", "checked");
            fillLangSetById("PL_PRG_val", lang.name, lang.prg_hr_rel_short);
            return;
        case 2:
        case "2":
            $("#D_hra_val").attr("checked", "checked");
            fillLangSetById("PL_PRG_val", lang.name, lang.prg_hr_abs_short);
            return;
        case 3:
        case "3":
            $("#D_col_val").attr("checked", "checked");
            fillLangSetById("PL_PRG_val", lang.name, lang.prg_cooling_short);
            return;
        case 4:
        case "4":
            $("#D_co2_val").attr("checked", "checked");
            fillLangSetById("PL_PRG_val", lang.name, lang.prg_co2_short);
            return;
        case 5:
        case "5":
            $("#D_win_val").attr("checked", "checked");
            fillLangSetById("PL_RED_val", lang.name, lang.water_ins_short);
            return;
        case 6:
        case "6":
            $("#D_otb_val").attr("checked", "checked");
            fillLangSetById("PL_RED_val", lang.name, lang.prg_out_temp_short);
            return;
        case 7:
        case "7":
            $("#D_hin_val").attr("checked", "checked");
            fillLangSetById("PL_RED_val", lang.name, lang.prg_hum_ins_short);
            return;
        default:
            return
        }
    })
}
function setOMdetails(State, ControlAuto, defrostExhaust, humRedMode) {
    langs.forEach(function(lang) {
        switch (State) {
        case 0:
        case "0":
        case 1:
        case "1":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Comfort";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "cmf";
            setProgramCheckbox(ControlAuto, defrostExhaust);
            break;
        case 2:
        case "2":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Sleep";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "slp";
            break;
        case 3:
        case "3":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Turbo";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "trb";
            break;
        case 4:
        case "4":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Turbo Cool";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "trc";
            break;
        case 5:
        case "5":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Service";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "srv";
            break;
        case 6:
        case "6":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Test";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "tst";
            break;
        case 7:
        case "7":
            document.getElementById("D_OM_val_" + lang.name).innerHTML = "Manufacturer";
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = "mnu";
            break
        }
        if (humRedMode) {
            document.getElementById("D_OM_val_" + lang.name).innerHTML = lang.om_hum_red_long;
            document.getElementById("PL_OM_val_" + lang.name).innerHTML = lang.om_hum_red_short
        }
    })
}
function fillLangSetById(idCore, langname, wort) {
    $("#" + idCore + "_" + langname).text(wort)
}
function fillMinuteTable(blobsarray0, SNR) {
    langs.forEach(function(lang) {
        $("#PL_TIM_val").text(parseTimestamp(blobsarray0["timestamp"], true));
        if (blobsarray0["HumRedMode"] == 0 || blobsarray0["HumRedMode"] == "0") {
            fillLangSetById("PL_HR_val", lang.name, lang.no)
        } else {
            fillLangSetById("PL_HR_val", lang.name, lang.yes)
        }
        if (blobsarray0["bSumCooling"] == 0 || blobsarray0["bSumCooling"] == "0") {
            fillLangSetById("PL_SC_val", lang.name, lang.no)
        } else {
            fillLangSetById("PL_SC_val", lang.name, lang.yes)
        }
    });
    $("#PL_CL_val").text(blobsarray0["ComfortLevel"]);
    $("#PL_RA_val").text(blobsarray0["RoomArea"]);
    $("#PL_2A_val").text(blobsarray0["SecondRoomFlow"]);
    $("#PL_FSS_val").text(blobsarray0["FanSupplyRPM"]);
    $("#PL_FSE_val").text(blobsarray0["FanExtractRPM"]);
    $("#PL_AFL_val").text(blobsarray0["AirFlow"]);
    $("#PL_TET_val").text(blobsarray0["TempExtract"].toFixed(1));
    $("#PL_HET_val").text(blobsarray0["HumExtract"]);
    $("#PL_TOU_val").text(blobsarray0["TempOutdoor"].toFixed(1));
    $("#PL_HOU_val").text(blobsarray0["HumOutdoor"]);
    $("#PL_CO2_val").text(blobsarray0["CO2"]);
    $("#PL_TSU_val").text(blobsarray0["TempSupply"].toFixed(1));
    $("#PL_TSC_val").text(blobsarray0["TempVirtSupExit"].toFixed(1));
    $("#PL_TEH_val").text(blobsarray0["TempExhaust"].toFixed(1));
    $("#PL_APR_val").text(blobsarray0["Pressure"]);
    $("#PL_ADY_val").text(blobsarray0["airDensity"]);
    $("#PL_HRP_val").text(getHeatRecoveryPercentage(blobsarray0["TempExtract"], blobsarray0["TempOutdoor"], blobsarray0["TempSupply"], blobsarray0["AirFlow"]));
    $("#PL_HRW_val").text(getPowerRecovery(blobsarray0["TempExtract"], blobsarray0["TempOutdoor"], blobsarray0["TempSupply"], blobsarray0["AirFlow"]));
    $("#PL_OPH_val").text(blobsarray0["operating_hours"]);
    $("#PL_FIH_val").text(blobsarray0["filter_hours"]);
    $("#PL_SNR_val").text(SNR);
    if (blobsarray0["ErrorState"] == 0 || blobsarray0["ErrorState"] == "0" || (blobsarray0["ErrorState"] == 22 || blobsarray0["ErrorState"] == "22")) {
        noError()
    } else {
        fillErrorText(blobsarray0["ErrorState"])
    }
    document.getElementById("PL_EFN_val").innerText = blobsarray0["ErrorFileNr"];
    $("#PL_ELN_val").text(blobsarray0["ErrorLineNr"]);
    $("#PL_ECO_val").text(blobsarray0["ErrorCode"]);
    $("#PL_VPE_val").text(blobsarray0["VentPosExtract"]);
    $("#PL_VBY_val").text(blobsarray0["VentPosBypass"]);
    $("#PL_VBA_val").text(blobsarray0["VentPosBath"]);
    $("#PL_VPS_val").text(blobsarray0["VentPosSupply"]);
    $("#PL_TPE_val").text(blobsarray0["CtrlSetExtVent"]);
    $("#PL_TBY_val").text(blobsarray0["CtrlSetBypVent"]);
    $("#PL_TBA_val").text(blobsarray0["CtrlSet2ndVent"]);
    $("#PL_TPS_val").text(blobsarray0["CtrlSetSupVent"]);
    $("#PL_FSF_val").text(blobsarray0["FilterSupplyFul"]);
    $("#PL_FEF_val").text(blobsarray0["FilterExtractFul"]);
    document.getElementById("PL_DIP_val").innerText = blobsarray0["DIPSwitch"];
    $("#PL_FSC_val").text(blobsarray0["FSC"]);
    $("#PL_FEC_val").text(blobsarray0["FEC"]);
    $("#PL_CSU_val").text(blobsarray0["CSU"]);
    $("#PL_CFA_val").text(blobsarray0["CFA"]);
    $("#PL_RSSI_val").text(blobsarray0["RSSI"]);
    $("#PL_S1_val").text(blobsarray0["S1"]);
    $("#PL_S2_val").text(blobsarray0["S2"]);
    $("#PL_S3_val").text(blobsarray0["S3"]);
    $("#PL_S4_val").text(blobsarray0["S4"]);
    $("#PL_S5_val").text(blobsarray0["S5"]);
    $("#PL_S6_val").text(blobsarray0["S6"])
}
function getPowerRecovery(tempExtract, tempOutdoor, tempSupply, airFlow) {
    if (Math.abs(tempExtract - tempOutdoor) < 2) {
        return 0
    }
    var recovery1 = airFlow * (tempSupply - tempOutdoor);
    return (recovery1 / 3 + .5).toFixed(1)
}
function getHeatRecoveryPercentage(tempExtract, tempOutdoor, tempSupply, airFlow) {
    if (airFlow == 0) {
        return 100
    }
    if (Math.abs(tempExtract - tempOutdoor) < 2) {
        return 100
    }
    var val = 100 * (1 - (tempExtract - tempSupply) / (tempExtract - tempOutdoor)) + .5;
    return val.toFixed(1)
}
function hasClass(element, cls) {
    return (" " + element.className + " ").indexOf(" " + cls + " ") > -1
}
function traffic_lights(blobsarray0) {
    if (blobsarray0["HumExtract"] != undefined) {
        if (blobsarray0["HumExtract"] < 10 || blobsarray0["HumExtract"] > 85) {
            $("#OV_traffic_lights_humidity :nth-child(4)").addClass("active")
        } else if (blobsarray0["HumExtract"] < 20 || blobsarray0["HumExtract"] > 70) {
            $("#OV_traffic_lights_humidity :nth-child(3)").addClass("active")
        } else if (blobsarray0["HumExtract"] < 30 || blobsarray0["HumExtract"] > 60) {
            $("#OV_traffic_lights_humidity :nth-child(2)").addClass("active")
        } else {
            $("#OV_traffic_lights_humidity :nth-child(1)").addClass("active")
        }
    }
    if (blobsarray0["CO2"] != undefined) {
        if (blobsarray0["CO2"] < 1e3) {
            $("#OV_traffic_lights_CO2 :nth-child(1)").addClass("active")
        } else if (blobsarray0["CO2"] < 1700) {
            $("#OV_traffic_lights_CO2 :nth-child(2)").addClass("active")
        } else if (blobsarray0["CO2"] < 2500) {
            $("#OV_traffic_lights_CO2 :nth-child(3)").addClass("active")
        } else {
            $("#OV_traffic_lights_CO2 :nth-child(4)").addClass("active")
        }
    }
    if (blobsarray0["FanSupplyRPM"] != undefined && blobsarray0["FanSpeed"]) {
        filterSupplyStatus(blobsarray0["FanSupplyRPM"], blobsarray0["FanSpeed"])
    }
    if (blobsarray0["FanExtractRPM"] != undefined && blobsarray0["FanSpeed"]) {
        filterExtractStatus(blobsarray0["FanExtractRPM"], blobsarray0["FanSpeed"])
    }
}
function filterExtractStatus(fanExtractRPM, fanSpeed) {
    var fanExtractRPMs = {};
    fanExtractRPMs[0] = [20, 920, 1560];
    fanExtractRPMs[1] = [30, 1040, 1680];
    fanExtractRPMs[2] = [40, 1260, 1900];
    fanExtractRPMs[3] = [50, 1480, 2200];
    fanExtractRPMs[4] = [60, 1700, 2420];
    fanExtractRPMs[5] = [70, 1910, 2710];
    fanExtractRPMs[6] = [85, 2210, 2930];
    fanExtractRPMs[7] = [100, 2480, 3200];
    fanExtractRPMs[8] = [0, 0, 0];
    var status = filterStatus(fanExtractRPM, fanSpeed, fanExtractRPMs);
    switch (status) {
    case 1:
        $("#OV_tl_ef :nth-child(1)").addClass("active");
        break;
    case 2:
        $("#OV_tl_ef :nth-child(2)").addClass("active");
        break;
    case 3:
        $("#OV_tl_ef :nth-child(3)").addClass("active");
        break;
    case 4:
        $("#OV_tl_ef :nth-child(4)").addClass("active");
        break;
    default:
        break
    }
}
function filterSupplyStatus(fanSupplyRPM, fanSpeed) {
    var fanSupplyRPMs = {};
    fanSupplyRPMs[0] = [20, 870, 1510];
    fanSupplyRPMs[1] = [30, 1e3, 1640];
    fanSupplyRPMs[2] = [40, 1230, 1870];
    fanSupplyRPMs[3] = [50, 1460, 2100];
    fanSupplyRPMs[4] = [60, 1690, 2410];
    fanSupplyRPMs[5] = [70, 1910, 2630];
    fanSupplyRPMs[6] = [85, 2230, 2950];
    fanSupplyRPMs[7] = [100, 2540, 3260];
    fanSupplyRPMs[8] = [0, 0, 0];
    var status = filterStatus(fanSupplyRPM, fanSpeed, fanSupplyRPMs);
    switch (status) {
    case 1:
        $("#OV_tl_sf :nth-child(1)").addClass("active");
        break;
    case 2:
        $("#OV_tl_sf :nth-child(2)").addClass("active");
        break;
    case 3:
        $("#OV_tl_sf :nth-child(3)").addClass("active");
        break;
    case 4:
        $("#OV_tl_sf :nth-child(4)").addClass("active");
        break;
    default:
        break
    }
}
function filterStatus(fanRPM, fanSpeed, filterRPMs) {
    fanSpeed = fanSpeed * 10;
    for (var i = 0; filterRPMs[i][0]; i++) {
        if (filterRPMs[i][0] < fanSpeed) {
            continue
        }
        var nDiff = filterRPMs[i][2] - filterRPMs[i][1];
        if (fanRPM < filterRPMs[i][1] - nDiff / 2)
            return 100;
        if (fanRPM < filterRPMs[i][1] + nDiff * .4)
            return 1;
        if (fanRPM < filterRPMs[i][1] + nDiff * .7)
            return 2;
        if (fanRPM < filterRPMs[i][1] + nDiff * .95)
            return 3;
        return 4
    }
}
function setDefaultValuesOverview() {
    $("#outdoor_temp_val").text("-5");
    $("#outdoor_hum_rel_val").text("50");
    $("#outdoor_hum_abs_val").text("2.5");
    $("#exhaust_temp_val").text("5");
    $("#extract_temp_val").text("21");
    $("#extract_hum_rel_val").text("50");
    $("#extract_hum_abs_val").text("5.2");
    $("#extract_CO2_val").text("900");
    $("#air_flow_val").text("30");
    $("#supply_temp_val").text("19");
    $("#error").text("");
    $("#heat_recovery_val").text("92");
    $("#power_recovery_val").text("230");
    $("#OV_traffic_lights_humidity :nth-child(1)").addClass("active");
    $("#OV_traffic_lights_CO2 :nth-child(1)").addClass("active");
    $("#OV_tl_ef :nth-child(2)").addClass("active");
    $("#OV_tl_sf :nth-child(2)").addClass("active");
    log_array.forEach(function(log) {
        document.getElementById(log.name + "_values").style.display = "none"
    });
    makeHeatRecoveryVisible();
    handlePopup()
}
function getCoolingPower(airFlow, tempExtract, tempSupply) {
    return (airFlow * (tempExtract - tempSupply) / 3 + .5).toFixed(1)
}
function fillErrorText(err) {
    if (err == 22) {
        noError();
        return
    }
    localStorage.setItem("error", err);
    var serObject = "err=" + err + "&serialnumber=" + getSNR() + "&device=1";
    $.ajax({
        method: "POST",
        data: {
            serObject: serObject
        },
        url: "./getErrorTextLong.php",
        success: function(data) {
            setError(data)
        }
    })
}
function setError(data) {
    errorArrLangShort = data.split("trans");
    errorArrLang = errorArrLangShort[0].split("&");
    errorArrShort = errorArrLangShort[1].split("&");
    langs.forEach(function(lang) {
        errorLang = errorArrLang[lang.column_nr].split("=");
        $("#error_msg_" + lang.name).text(prepareTextFromDB(errorLang[1]));
        errorShort = errorArrShort[lang.column_nr].split("=");
        $("#PL_ES_val_" + lang.name).text(prepareTextFromDB(errorShort[1]))
    });
    document.getElementById("error_div").style.display = "block";
    var error = localStorage.getItem("error");
    if (error == 1 || error == 2 || error == 20) {
        document.getElementById("switch-off").style.display = "none"
    }
}
function makeHeatRecoveryVisible() {
    document.getElementById("heat_recovery_p").style.display = "block";
    document.getElementById("power_recovery_p").style.display = "block";
    document.getElementById("OV_heat_recovery").style.display = "block";
    document.getElementById("OV_power_recovery").style.display = "block"
}
function noError() {
    langs.forEach(function(lang) {
        $("#PL_ES_val_" + lang.name).text("OK")
    });
    document.getElementById("error_div").style.display = "none"
}
