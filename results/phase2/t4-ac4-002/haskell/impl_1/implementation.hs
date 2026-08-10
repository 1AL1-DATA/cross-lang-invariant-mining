import Data.Char (isDigit, isSpace)
import Text.Read (readMaybe)

data Token = Num Int | Plus | Minus | Times | Divide | LParen | RParen
    deriving (Show, Eq)

lexer :: String -> Maybe [Token]
lexer [] = Just []
lexer (c:cs)
    | isSpace c = lexer cs
    | isDigit c = lexNum (c:cs)
    | c == '+' = (Plus :) <$> lexer cs
    | c == '-' = (Minus :) <$> lexer cs
    | c == '*' = (Times :) <$> lexer cs
    | c == '/' = (Divide :) <$> lexer cs
    | c == '(' = (LParen :) <$> lexer cs
    | c == ')' = (RParen :) <$> lexer cs
    | otherwise = Nothing
  where
    lexNum s = let (numStr, rest) = span isDigit s
               in case readMaybe numStr of
                   Just n -> (Num n :) <$> lexer rest
                   Nothing -> Nothing

parser :: [Token] -> Maybe Int
parser tokens = case parseExpr tokens of
    Just (result, []) -> Just result
    _ -> Nothing

parseExpr :: [Token] -> Maybe (Int, [Token])
parseExpr tokens = do
    (val, rest) <- parseTerm tokens
    parseExpr' val rest

parseExpr' :: Int -> [Token] -> Maybe (Int, [Token])
parseExpr' val (Plus:rest) = do
    (val2, rest2) <- parseTerm rest
    parseExpr' (val + val2) rest2
parseExpr' val (Minus:rest) = do
    (val2, rest2) <- parseTerm rest
    parseExpr' (val - val2) rest2
parseExpr' val tokens = Just (val, tokens)

parseTerm :: [Token] -> Maybe (Int, [Token])
parseTerm tokens = do
    (val, rest) <- parseFactor tokens
    parseTerm' val rest

parseTerm' :: Int -> [Token] -> Maybe (Int, [Token])
parseTerm' val (Times:rest) = do
    (val2, rest2) <- parseFactor rest
    parseTerm' (val * val2) rest2
parseTerm' val (Divide:rest) = do
    (val2, rest2) <- parseFactor rest
    parseTerm' (val `div` val2) rest2
parseTerm' val tokens = Just (val, tokens)

parseFactor :: [Token] -> Maybe (Int, [Token])
parseFactor (Num n:rest) = Just (n, rest)
parseFactor (LParen:rest) = case parseExpr rest of
    Just (val, RParen:rest2) -> Just (val, rest2)
    _ -> Nothing
parseFactor _ = Nothing

evaluate :: String -> Maybe Int
evaluate s = lexer s >>= parser