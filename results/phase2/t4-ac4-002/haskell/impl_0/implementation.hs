module Parser where

import Data.Char (isDigit)

data Token = Num Int | Plus | Minus | Times | Div | LParen | RParen
    deriving (Show, Eq)

tokenize :: String -> [Token]
tokenize [] = []
tokenize (c:cs)
    | isDigit c = let (num, rest) = span isDigit (c:cs) 
                  in Num (read num) : tokenize rest
    | c == '+' = Plus : tokenize cs
    | c == '-' = Minus : tokenize cs
    | c == '*' = Times : tokenize cs
    | c == '/' = Div : tokenize cs
    | c == '(' = LParen : tokenize cs
    | c == ')' = RParen : tokenize cs
    | c == ' ' = tokenize cs
    | otherwise = tokenize cs

parseExpr :: [Token] -> (Int, [Token])
parseExpr = parseAdd

parseAdd :: [Token] -> (Int, [Token])
parseAdd tokens = 
    let (left, rest) = parseMul tokens
    in case rest of
        (Plus:t) -> let (right, rest') = parseAdd t in (left + right, rest')
        (Minus:t) -> let (right, rest') = parseAdd t in (left - right, rest')
        _ -> (left, rest)

parseMul :: [Token] -> (Int, [Token])
parseMul tokens = 
    let (left, rest) = parsePrimary tokens
    in case rest of
        (Times:t) -> let (right, rest') = parseMul t in (left * right, rest')
        (Div:t) -> let (right, rest') = parseMul t in (left `div` right, rest')
        _ -> (left, rest)

parsePrimary :: [Token] -> (Int, [Token])
parsePrimary (Num n : rest) = (n, rest)
parsePrimary (LParen : rest) = 
    let (val, rest') = parseExpr rest
    in case rest' of
        (RParen : r) -> (val, r)
        _ -> error "Missing closing parenthesis"
parsePrimary _ = error "Invalid expression"

evaluate :: String -> Int
evaluate s = let tokens = tokenize s
                 (result, _) = parseExpr tokens
             in result