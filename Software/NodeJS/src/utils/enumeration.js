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
