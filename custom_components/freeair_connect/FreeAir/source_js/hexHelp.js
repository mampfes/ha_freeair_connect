function lowPlusHigh(low, high, superHigh) {
    var arBitsTotal = [];
    for (var i = 0; i < 21; i++) {
        arBitsTotal.push(0)
    }
    var LSB7 = byteToBits(low, 0);
    var MSB7;
    for (var i = 0; i < 7; i++) {
        arBitsTotal[i] = LSB7[i]
    }
    if (superHigh != undefined) {
        MSB7 = byteToBits(high, 0);
        if (MSB7.length != 8) {}
        for (var i = 0; i < 7; i++) {
            arBitsTotal[i + 7] = MSB7[i]
        }
        var superHighBit = 0;
        for (var i = 14; i < superHigh.length + 14; i++) {
            arBitsTotal[i] = superHigh[superHighBit];
            superHighBit = superHighBit + 1
        }
    } else {
        var highBit = 0;
        for (var i = 7; i < high.length + 7; i++) {
            arBitsTotal[i] = high[highBit];
            highBit = highBit + 1
        }
    }
    var value = 0;
    var potenz = 1;
    for (var i = 0; i < 20; i++) {
        value = value + arBitsTotal[i] * potenz;
        potenz = potenz * 2
    }
    return value
}
function divideByte(division, byte) {
    var bits = byteToBits(byte, 0);
    var dividedByte = [];
    var bit = 0;
    for (var i = 0; i < division.length; i++) {
        dividedByte[i] = [];
        for (var b = 0; b < division[i]; b++) {
            dividedByte[i].push(bits[bit]);
            bit += 1
        }
    }
    if (bit != 8) {}
    var checkSumByte = 0;
    for (var i = 0; i < division.length; i++) {
        checkSumByte += dividedByte[i].length
    }
    if (checkSumByte != 7) {}
    return dividedByte
}
function byteToBits(byte, firstBit) {
    var bits = [0, 0, 0, 0, 0, 0, 0, 0];
    var potenz = 128;
    for (var i = 7; i >= 0; i--) {
        if (byte / potenz >= 1) {
            bits[i] = 1;
            byte = byte - potenz;
            if (i == 0 && byte > 0) {}
        }
        potenz = potenz / 2
    }
    return bits
}
function getNumberFrBits(arBits, uCount) {
    var potenz = 1;
    var uNumber = 0;
    for (var i = 0; i < arBits.length; i++) {
        uNumber += arBits[i] * potenz;
        potenz = potenz * 2
    }
    return uNumber
}
function getPressure(Pressure5MSB, Pressure4LSB) {
    var arBitsTotal = [];
    for (var i = 0; i < 21; i++) {
        arBitsTotal.push(0)
    }
    for (var i = 0; i < 4; i++) {
        arBitsTotal[i] = Pressure4LSB[i]
    }
    for (var i = 0; i < 5; i++) {
        arBitsTotal[i + 4] = Pressure5MSB[i]
    }
    var value = 0;
    var potenz = 1;
    for (var i = 0; i < 20; i++) {
        value = value + arBitsTotal[i] * potenz;
        potenz = potenz * 2
    }
    return value + 700
}
