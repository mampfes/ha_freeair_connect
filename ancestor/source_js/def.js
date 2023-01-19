var log_array = [
    {
        name        : "daily",
        sec_type    : 2,
        classletter : "T",
        tab_place   : 12,
        place_1     : 4,
        place_2     : 5,
        place_3     : 6,
        place_4     : 7, 
        id_name     : "TV_",
        aircoef     : 3.556,
        Tcoef       : 1,
        enecoef     : 42.7,
        watercoef   : 128,
        DLmax       : 24,
        opho        : 24,
        id_tab      : "nav5"
    },
    {
        name        : "monthly",
        sec_type    : 3,
        classletter : "M",
        tab_place   : 13,
        place_1     : 8,
        place_2     : 9,
        place_3     : 10,
        place_4     : 11,
        id_name     : "MV_",
        aircoef     : 113.8,
        Tcoef       : 24,
        enecoef     : 1365,
        watercoef   : 4096,
        DLmax       : 720,
        opho        : 720,
        id_tab      : "nav6"

    }
];

var $blobsArraySecLogDaily = [];
var $blobsArraySecLogMonthly = [];



var langs = [
    {
        name                 : "de",
        lang_nr              : 1,
        showPwd              : "<a onclick='showPwd()'>Passwort anzeigen</a>",
        hidePwd              : "<a onclick='hidePwd()'>Passwort verstecken</a>",
        cl_popover_content   : "Bitte geben Sie die Seriennummer Ihres Ger&auml;tes ein.",
        id_flag              : "flag_de",
        flag_file_name       : "de.png",
        column_nr            : 2,
        no                   : "nein",
        yes                  : "ja",
        prg_water_ins_short  : "wet",
        prg_cooling_short    : "kuh",
        prg_co2_short        : "co2",
        prg_min_vent_short   : "mnl",
        prg_hr_rel_short     : "efr",
        prg_hr_abs_short     : "efa",
        prg_hum_ins_short    : "fet",
        prg_out_temp_short   : "alu",
        om_hum_red_long      : "Entfeuchtung",
        om_hum_red_short     : "hrd",  //TODO
        key_edit_placeholder : "fAPasswort"
        
    },
    {
        name                 : "en",
        lang_nr              : 2,
        showPwd              : "<a onclick='showPwd()'>Show password</a>",
        hidePwd              : "<a onclick='hidePwd()'>Hide password</a>",
        cl_popover_content   : "Please enter the serial number of your device.",
        id_flag              : "flag_en",
        flag_file_name       : "eng.png",
        column_nr            : 1,
        no                   : "no",
        yes                  : "yes",
        prg_water_ins_short  : "win",
        prg_cooling_short    : "col",
        prg_co2_short        : "co2",
        prg_min_vent_short   : "mve",
        prg_hr_rel_short     : "hrr",
        prg_hr_abs_short     : "hra",
        prg_hum_ins_short    : "hin",
        prg_out_temp_short   : "otb",
        om_hum_red_long      : "Hum.Reduction",
        om_hum_red_short     : "hrd",
        key_edit_placeholder : "Key"
    }
];


var $secLogHeader =
[
    ['TIM',''],
    ['RES',''],
    ['TET','[°C]'],
    ['HET','[%]'],
    ['TOU','[°C]'],
    ['HOU','[%]'],
    ['CO2','[ppm]'],
    ['TSU','[°C]'],
    ['TEH','[°C]'],
    ['APR','[hPa]'],
    ['ADY','[kg/m3]'],
    ['HRP','[%]'],
    ['SNR',''],
    ['DL1','[S:M]'],
    ['DL2','[S:M]'],
    ['DL3','[S:M]'],
    ['DL4','[S:M]'],
    ['DL5','[S:M]'],
    ['DSM','[S:M]'],
    ['DTM','[S:M]'],
    ['D1R','[S:M]'],
    ['DDF','[S:M]'],
    ['DMV','[S:M]'],
    ['DWI','[S:M]'],
    ['DHI','[S:M]'],
    ['DRA','[S:M]'],
    ['DRR','[S:M]'],
    ['DCO','[S:M]'],
    ['DC2','[S:M]'],
    ['HRU',''],
    ['HRN',''],
    ['EXE','[Wh]'],
    ['REE','[Wh]'],
    ['PCO','[Wh]'],
    ['COE','[Wh]'],
    ['AEX','[m3]'],
    ['WAR','[g]'],
    ['ES' ,''],
    ['EFN',''],
    ['ELN',''],
    ['ECO',''],
    ['FSF',''],
    ['FEF',''],
    ['S21',''],
    ['S22',''],
    ['S23',''],
    ['S24',''],
    ['S25',''],
    ['S26',''],
    ['S27',''],
    ['S28',''],
    ['S29',''],
    ['S30', '']
]


var $diagramList =
[
    ['TET', 1, "#f3e500"], // remain
    ['HET', 2, "#FF7733"], // orange
    ['TOU', 1, "#01db8b"], // navy blue
    ['HOU', 2, "#672011"], 
    ['CO2', 3, "#000080"], 
    ['TSU', 1, "#f3e500"],
    ['TEH', 1, "#dfab62"], 
    ['APR', 4, "#ef5253"], // red
    ['ADY', 5, "#FF33F9"], // violet
    ['HRP', 2, "#FF3371"], 
    ['EXE', 6, "#177612"], // dark green
    ['REE', 6, "#3CFF33"],
    ['PCO', 6, "#AFFF33"], 
    ['COE', 6, "#900db0"], // violet 
    ['AEX', 7, "#FF33D4"], // rosa
    ['WAR', 8, "#33FFFF"] 
]

var mapUnits = 
[
    [0, ''          , ''        , 10000 , 10000 ],
    [1, '[°C]'      , '°C'      , -50   , 100   ],
    [2, '[%]'       , '%'       , 0     , 100   ],
    [3, '[ppm]'     , 'ppm'     , 300   , 5000  ],
    [4, '[hPa]'     , 'hPa'     , 10000 , 10000 ],
    [5, '[kg/m3]'   , 'kg/m3'   , 10000 , 10000 ],
    [6, '[Wh]'      , 'Wh'      , 10000 , 10000 ],
    [7, '[m3]'      , 'm3'      , 10000 , 10000 ],
    [8, '[g]'       , 'g'       , 10000 , 10000 ]
];


var $chosenUnits = [];

const DEFAULT_LANG_NAME   = "en";
const MAGIC_WORD_TRANSLATION = "rrrsssttt";

const HIDE = 1;
const SHOW = 2;


const PRIM_LOG_PLACE_1 = 0;
const PRIM_LOG_PLACE_2 = 1;
const PRIM_LOG_PLACE_3 = 2;
const PRIM_LOG_PLACE_4 = 3;


const PLAUSI_TEMP_MAX =  100;
const PLAUSI_TEMP_MIN =  -50;
const PLAUSI_HUM_MAX  =  100;
const PLAUSI_HUM_MIN  =    0;
const PLAUSI_AIR_MAX  =  150;
const PLAUSI_AIR_MIN  =    0;
const PLAUSI_WRP_MAX  =  110;
const PLAUSI_WRP_MIN  =    0;
const PLAUSI_CO2_MAX  = 6000;
const PLAUSI_CO2_MIN  =    1;

const SRN_RELOAD      = 10;

const TRANS_ALLG      = 1;
const TRANS_SECLOG    = 2;


const DG_DAYS_30            = 1;
const DG_DAYS_100           = 2;
const DG_MONTHS             = 3;
const DG_DAYS_AND_MONTHS    = 4;



// create object line chart data, must be global
var lineChartData = {};
