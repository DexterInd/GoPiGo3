// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const _ = require('lodash');
const path = require('path');
const i2c = require('i2c-bus');
const fs = require('fs');
const math = require('mathjs');

const i2c0Path  = '/dev/i2c-0';
const i2c1Path  = '/dev/i2c-1';

class LineFollow {
    bus = 0;
    busNumber = 0;

    address   = 0x06;
    aReadCmd = 3;
    unused = 0;
    multp = [-10, -5, 0, 5, 10];
    whiteLine = [0, 0, 0, 0, 0];
    blackLine = [0, 0, 0, 0, 0];
    rangeCol = [0, 0, 0, 0, 0];

    fileB = path.join(__dirname, '/blackLine.txt');
    fileW = path.join(__dirname, '/whiteLine.txt');
    fileR = path.join(__dirname, '/rangeLine.txt');

    sensorBuffer = [[], [], [], [], []];
    maxBufferLength = 20;

    constructor() {
        console.log('LineFollow init');

        if (fs.existsSync(i2c0Path)) {
            this.busNumber = 0;
        } else if (fs.existsSync(i2c1Path)) {
            this.busNumber = 1;
        } else {
            throw new Error('GrovePI could not determine your i2c device');
        }

        this.bus = i2c.openSync(this.busNumber);
    }

    _eliminateNoise(values, stdFactor = 2) {
        const mean = math.mean(values);
        const standardDeviation = math.std(values);
        let output = [];

        if (standardDeviation === 0) {
            return values;
        }

        output = _.map(values, v => v > mean - (stdFactor * standardDeviation));
        output = _.map(output, v => v < mean - (stdFactor * standardDeviation));

        return output;
    }

    writeI2cBlock(addr, block) {
        const buffer = new Buffer(block);
        let ret = false;
        try {
            const val = this.bus.i2cWriteSync(addr, buffer.length, buffer);
            ret = val > 0;
        } catch (err) {
            console.log(err);
            ret = false;
        }
        return ret;
    }

    absoluteLinePos() {
        const linePos = [0, 0, 0, 0, 0];
        const whiteLine = this.getWhiteLine();
        // const blackLine = this.getBlackLine();
        const rangeSensor = this.getRange();
        const threshold = _.map(whiteLine, (v, i) => v + (rangeSensor[i] / 2));
        const rawVals = this.getSensorVal();

        for (let i = 0, len = 5; i < len; i++) {
            if (rawVals[i] === -1) {
                linePos[i] = -1;
            } else if (rawVals[i] > threshold[i]) {
                linePos[i] = 1;
            } else {
                linePos[i] = 0;
            }
        }

        return linePos;
    }

    readSensor() {
        const output = [];

        this.bus.i2cWriteSync(this.address, 1,
            [this.aReadCmd, this.unused, this.unused, this.unused]
        );
        const buffer = new Buffer(10);
        this.bus.i2cReadSync(this.address, 10, buffer);

        for (let i = 0, len = 5; i < len; i++) {
            this.sensorBuffer[i].push((buffer[2 * i] * 256) + (buffer[(2 * i) + 1]));

            if (this.sensorBuffer[i].length > this.maxBufferLength) {
                this.sensorBuffer[i].pop();
            }

            let filteredValue = this._eliminateNoise(this.sensorBuffer[i], 2);
            filteredValue = filteredValue[filteredValue.length - 1];

            output.push(filteredValue);
        }

        return output;
    }

    resetBuffer() {
        this.sensorBuffer = [[], [], [], [], []];
    }

    getSensorVal() {
        let attempt = 0;
        let val = 0;

        while (attempt < 5) {
            val = this.readSensor();
            if (val[0] !== -1) {
                break;
            } else {
                val = this.readSensor();
                attempt++;
            }
        }

        return val;
    }

    setBlackLine() {
        let val;
        for (let i = 0, len = 5; i < len; i++) {
            val = this.readSensor();
        }

        if (val[0] !== -1) {
            this.blackLine = val;
        } else {
            this.blackLine = [-1, -1, -1, -1];
        }

        this.rangeCol = _.map(this.blackLine, (v, i) => v - this.whiteLine[i]);

        fs.writeFileSync(this.fileB, this.blackLine.join(','));

        fs.writeFileSync(this.fileR, this.rangeCol.join(','));
    }

    getBlackLine() {
        this.blackLine = fs.readFileSync(this.fileB, 'utf8');
        return _.map(this.blackLine.split(','), v => parseInt(v, 0));
    }

    setWhiteLine() {
        let val;
        for (let i = 0, len = 5; i < len; i++) {
            val = this.readSensor();
        }

        if (val[0] !== -1) {
            this.whiteLine = val;
        } else {
            this.whiteLine = [-1, -1, -1, -1];
        }

        this.rangeCol = _.map(this.blackLine, (v, i) => v - this.whiteLine[i]);
        fs.writeFileSync(this.fileW, this.whiteLine.join(','));

        fs.writeFileSync(this.fileR, this.rangeCol.join(','));
    }

    getWhiteLine() {
        this.whiteLine = fs.readFileSync(this.fileW, 'utf8');
        return _.map(this.whiteLine.split(','), v => parseInt(v, 0));
    }

    getRange() {
        this.rangeCol = fs.readFileSync(this.fileR, 'utf8');
        return _.map(this.rangeCol.split(','), v => parseInt(v, 0));
    }

    linePosition() {
        this.blackLine = this.getBlackLine();
        this.whiteLine = this.getWhiteLine();
        this.rangeCol = this.getRange();

        const curr = this.getSensorVal();
        const diffVal = _.map(this.whiteLine, v => curr - v);
        let currPos = 0;
        const percentBlackLine = [0, 0, 0, 0, 0];

        for (let i = 0, len = 5; i < len; i++) {
            percentBlackLine[i] = (diffVal[i] * 100) / this.rangeCol[i];
            currPos += percentBlackLine[i] * this.multp[i];
        }

        return currPos;
    }
}

module.exports = LineFollow;
