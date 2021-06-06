import numpy as np
import pandas as pd
import time
import chess
from tqdm import tqdm

USED_THEMES = {
    "advancedPawn", "advantage", "bishopEndgame", "capturingDefender", "crushing", "equality", "kingsideAttack", "defensiveMove", "endgame",
    "exposedKing", "fork", "hangingPiece", "interference", "knightEndgame", "middlegame", "opening", "pawnEndgame", "pin", "promotion", "queenEndgame",
    "queenRookEndgame", "queensideAttack", "rookEndgame", "skewer", "trappedPiece", "underPromotion", "xRayAttack", "zugzwang",
}

def main():
    print(f"Reading 'puzzle_batches/lichess_db_puzzle.csv'...")
    print()
    start = time.time()

    df = pd.read_csv(f'puzzle_batches/lichess_db_puzzle.csv')
    print('leu')

    df = df[['FEN','Moves','Themes']].dropna()
    print('oi')

    out_df = create_out_df(df)
    print(out_df)
    for row in tqdm(df.itertuples()):
        encode_fen(row, out_df)
        encode_themes(row, out_df)

    out_df.to_csv(f'cleaned_puzzle_batches/cleaned_lichess_db_puzzle.csv',
                index=False)


    end = time.time()
    duration = end - start
    print("exec time: %.4fs" % duration)


def create_out_df(df):
    squares = chess.SQUARE_NAMES
    columns = []

    # pawn, knight, bishop, rook, king
    pieces = ['p', 'n', 'b', 'r', 'k'] 
    for s in squares:
        for p in pieces:
            columns.append(f"{s}.{p}")

    columns.append('color_to_play')
    columns += [f"theme_{theme}" for theme in USED_THEMES]

    out_df = pd.DataFrame(0, index=np.arange(len(df)), columns=columns, dtype=np.int8)

    return out_df


def encode_themes(row, df):
    row_themes = set(row.Themes.split())
    valid_themes = row_themes.intersection(USED_THEMES)

    for t in valid_themes:
        df.at[row.Index, f"theme_{t}"] = 1


def encode_fen(row, df):
    board = chess.Board(row.FEN)
    computer_move = row.Moves.split()[0]
    board.push_uci(computer_move)

    df.at[row.Index, "color_to_play"] = int(board.turn) or -1

    # color: false = preto / true = branco
    for pos, piece in board.piece_map().items():
        square_name = chess.square_name(pos)
        piece_name = piece.symbol().lower()

        if piece_name == "q":
            df.at[row.Index, f"{square_name}.r"] = 1 if piece.color else -1
            df.at[row.Index, f"{square_name}.b"] = 1 if piece.color else -1
        else:
            df.at[row.Index, f"{square_name}.{piece_name}"] = 1 if piece.color else -1

    return df


if __name__ == "__main__":
    main()
