function anagramDetection(s1: string, s2: string): boolean {
    const sortedS1 = s1.split('').sort().join('');
    const sortedS2 = s2.split('').sort().join('');
    return sortedS1 === sortedS2;
}

export default anagramDetection;