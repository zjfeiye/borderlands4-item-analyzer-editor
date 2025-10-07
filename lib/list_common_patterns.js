function extractPatternsToTest(str) {
    let patterns = [];
    for (let pos = 0; pos < str.length; pos++) {
        for (let length = 1; length <= str.length - pos; length++) {
            let pattern = str.substring(pos, pos + length);
            if (!patterns.includes(pattern)) patterns.push(pattern);
        }
    }

    return patterns;
}

function listCommonPatterns(str1, str2, minSize) {
    let patternsToTest = [];
    console.log('Extracting patterns from 1...')
    patternsToTest.push(...extractPatternsToTest(str1));
    console.log('  OK')
    console.log('Extracting patterns from 2...')
    patternsToTest.push(...extractPatternsToTest(str2));
    console.log('  OK')
    console.log('Total patterns to test: ', patternsToTest.length);

    // filter by min size
    patternsToTest = patternsToTest.filter(p => p.length >= minSize);

    let commonPatterns = [];
    let progress = 0;
    for (let pattern of patternsToTest) {
        let in1 = str1.indexOf(pattern);
        let in2 = str2.indexOf(pattern);
        if (in1 >= 0 && in2 >= 0) {
            if (!commonPatterns.includes(pattern)) {
                commonPatterns.push(pattern);
            }
        }
        progress++;

        if (progress % Math.floor(patternsToTest.length / 4) === 1)
            console.log('  ', Math.floor((progress / patternsToTest.length) * 100), '%');
    }
    console.log('Common patterns found: ', commonPatterns.length);
    return commonPatterns;
}

export {extractPatternsToTest, listCommonPatterns};