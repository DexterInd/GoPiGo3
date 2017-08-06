import { assert } from 'chai';
import awesomeFunction from '../src/awesomeModule';

describe('Awesome test.', () => {
  it('should test awesome function', () => {
    assert(awesomeFunction(1, 1) === 2, 'Not awesome :(');
  });
});
