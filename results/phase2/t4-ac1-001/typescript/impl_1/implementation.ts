function isAnagram(s1: string, s2: string): boolean {
    if (s1.length !== s2.length) {
        return false;
    }
    
    const sortString = (str: string): string => {
        return str.split('').sort().join('');
    };
    
    return sortString(s1) === sortString(s2);
}