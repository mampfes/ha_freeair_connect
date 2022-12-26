function getDataAjax(e, l, t, o) {
    $.ajax({
        method: "POST",
        data: {
            serObject: e
        },
        url: "./getDataHexAjax.php",
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "1728000"
        },
        success: function(e) {
            document.getElementById("sn").value = t;
            try {
                after(e, l, t, o)
            } catch (e) {
                console.log(e)
            }
        },
        error: function(e, l, t) {}
    }),
    getLang(getLangNow(), !1)
}
function after(e, l, t, o) {
    var n = []
      , a = decodeURIComponent(e).split("timestamp")
      , r = getObjectArrayPrimLog(l, a[PRIM_LOG_PLACE_1], a[PRIM_LOG_PLACE_2], a[PRIM_LOG_PLACE_3], a[PRIM_LOG_PLACE_4]);
    if (null != r)
        if (null != r[0]) {
            fillOverview(r[0]),
            fillDetails(r[0], t),
            fillMinuteTable(r[0], t);
            var c = 0;
            log_array.forEach(function(e) {
                var t = getObjectArraySecLog(l, a[e.place_1], a[e.place_2], a[e.place_3], a[e.place_4], e.sec_type, o);
                if (2 == e.sec_type) {
                    $blobsArraySecLogDaily = t;
                    localStorage.setItem("BlobsDaily", t)
                } else
                    $blobsArraySecLogMonthly = t;
                n[c] = t,
                c += 1;
                var r = decodeFromBase64(a[e.tab_place]);
                fillSecTab(t, e, r),
                null != t && null != document.getElementById("table_" + e.name) && null != document.getElementById("table_" + e.name) && (tableHeight = document.getElementById("table_" + e.name).offsetHeight),
                deleteEmptyTabSpace(e)
            }),
            getSecLogTrans(getLangNow(), !1),
            fillChart()
        } else
            log_array.forEach(function(e) {
                prepareForNoSecLog(e, "block", "none", "none")
            })
}
function getObjectArrayPrimLog(e, l, t, o, n) {
    var a = []
      , r = parseOneBlob(l, e)
      , c = {};
    if (checkPlausi(r) && (c = createPrimBlobObject(r, t, o, n),
    checkPlausiPrimBlob(c)))
        return a.push(c),
        a;
    document.getElementById("keyPopup").style.display = "block",
    log_array.forEach(function(e) {
        return prepareForNoSecLog(e, "none", "none", "block"),
        null
    })
}
function getObjectArraySecLog(e, l, t, o, n, a) {
    var r, c, s = [], i = 0, u = 0;
    if (log_array.forEach(function(e) {
        a == e.sec_type && (r = e)
    }),
    "NULL" == l || null == l)
        return prepareForNoSecLog(r, "block", "none", "none"),
        "NULL";
    document.getElementById("no_" + r.name + "_values").style.display = "none",
    document.getElementById(r.name + "_values").style.display = "block";
    var g = null;
    $("#" + r.name + "_values").jScrollPane(),
    c = $("#" + r.name + "_values").data("jsp"),
    reinitScroll(c, g),
    g = setTimeout(function() {
        c.reinitialise(),
        g = null
    }, 50),
    $(".table-scroll-horizontal").on("jsp-scroll-x", function(e, l, t, o) {
        $(this).find(".headcol").css({
            transform: "translateX(" + l + "px)"
        })
    });
    for (var m = l.split("&"), p = t.split("&"), _ = o.split("&"), f = n.split("&"), b = 0, d = 0; d < m.length; d++) {
        var y, L, h, O;
        i += 1,
        null != m[d] && (y = m[d].substr(m[d].indexOf("=") + 1)),
        null != p[d] && (L = p[d].substr(p[d].indexOf("=") + 1)),
        null != _[d] && (h = _[d].substr(_[d].indexOf("=") + 1)),
        null != f[d] && (O = f[d].substr(f[d].indexOf("=") + 1));
        var S = parseOneBlob(y, e)
          , P = checkPlausi(S)
          , A = {};
        1 == P && (A = createSecLogObject(S, L, h, O, r, SRN),
        P = checkPlausiSecBlob(A)),
        1 == P ? (s.push(A),
        b++) : u += 1
    }
    return localStorage.setItem("num_logs_" + r.name, i),
    localStorage.setItem("num_logs_not_plausi_" + r.name, u),
    0 == b && prepareForNoSecLog(r, "none", "block", "none"),
    s
}
