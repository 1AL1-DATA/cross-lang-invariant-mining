package wordcount

import (
    "strings"
)

func CountWords(lines []string) map[string]int {
    wordCounts := make(map[string]int)
    
    for _, line := range lines {
        words := splitIntoWords(line)
        for _, word := range words {
            lowerWord := strings.ToLower(word)
            wordCounts[lowerWord]++
        }
    }
    
    return wordCounts
}

func splitIntoWords(line string) []string {
    var words []string
    var currentWord strings.Builder
    
    for i := 0; i < len(line); i++ {
        if isWhitespace(line[i]) {
            if currentWord.Len() > 0 {
                words = append(words, currentWord.String())
                currentWord.Reset()
            }
        } else {
            currentWord.WriteByte(line[i])
        }
    }
    
    if currentWord.Len() > 0 {
        words = append(words, currentWord.String())
    }
    
    return words
}

func isWhitespace(c byte) bool {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r'
}