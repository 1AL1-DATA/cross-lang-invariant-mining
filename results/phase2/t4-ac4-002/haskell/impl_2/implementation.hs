module Parser where

import Data.Char (isDigit)

data Token = Number Int | Op Char
  deriving (Show)

tokenize :: String -> [Token]
tokenize [] = []
tokenize (c:cs)
  | isDigit c = let (num, rest) = span isDigit (c:cs)
                in Number (read num) : tokenize rest
  | c `elem` "+-*/()" = Op c : tokenize cs
  | c == ' ' = tokenize cs
  | otherwise = error $ "Invalid character: " ++ [c]

eval :: String -> Int
eval = parseExpr . tokenize

parseExpr :: [Token] -> Int
parseExpr tokens =
  let (result, rest) = parseAddSub tokens
  in if null rest
     then result
     else error "Unexpected input after valid expression"

parseAddSub :: [Token] -> (Int, [Token])
parseAddSub tokens =
  let (left, rest) = parseMulDiv tokens
  in case rest of
       (Op op : rest') | op `elem` "+-"
         -> let (right, rest'') = parseMulDiv rest'
            in case op of
                 '+' -> parseAddSub (Number (left + right) : rest'')
                 '-' -> parseAddSub (Number (left - right) : rest'')
       _ -> (left, rest)

parseMulDiv :: [Token] -> (Int, [Token])
parseMulDiv tokens =
  let (left, rest) = parseFactor