// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/DI_Sensors
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md

const Gopigo = require('./gopigo3');
const EasyGopigo = require('./easyGopigo3');

module.exports = {
    'Gopigo': Gopigo,
    'EasyGopigo': EasyGopigo
};
