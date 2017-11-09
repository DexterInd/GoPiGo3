// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/DI_Sensors
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md

const Gopigo3 = require('./gopigo3');
const EasyGopigo3 = require('./easyGopigo3');

module.exports = {
    'Gopigo3': Gopigo3,
    'EasyGopigo3': EasyGopigo3
};
