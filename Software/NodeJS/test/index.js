import { assert } from 'chai';
const EasyGopigo = require('../lib/easyGopigo3');
const gpg = new EasyGopigo();

describe('GoPiGo test.', () => {
  it('should test GoPiGo manufacturer', () => {
    assert(gpg.getManufacturer() === '', 'Empty manufacturer');
  });
});
