// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const _ = require('lodash');

class Enumeration {
    constructor(names) {
        const lines = names.split('\n');
        let number = 0;

        _.each(lines, (line) => {
            if (line.indexOf(',') >= 0) {
                // strip out the spaces + commas
                line = line.replace(/\s\s+/g, '').replace(',', '');

                if (line.indexOf('=') !== -1) {
                    const slices = line.split('=');
                    number = parseInt(slices[1], 0);
                    line = slices[0];
                }

                this[line] = number;
                number++;
            }
        });
    }
}

module.exports = Enumeration;
