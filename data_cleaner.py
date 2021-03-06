import pandas as pd
import time
import chess


USED_THEMES = {
    "advancedPawn", "advantage", "bishopEndgame", "capturingDefender", "crushing", "equality", "kingsideAttack", "defensiveMove", "endgame",
    "exposedKing", "fork", "hangingPiece", "interference", "knightEndgame", "middlegame", "opening", "pawnEndgame", "pin", "promotion", "queenEndgame",
    "queenRookEndgame", "queensideAttack", "rookEndgame", "skewer", "trappedPiece", "underPromotion", "xRayAttack", "zugzwang",
}

def main():
    #for n in range(1, 5):
    print(f"Reading 'puzzle_batches/validation_batch.csv'...")
    print()

    df = pd.read_csv(f'puzzle_batches/validation_batch.csv')
    df = df[['FEN','Moves','Themes']].dropna()
    df['valid_themes'] = ""

    df = create_board_positions_with_piece_vectors(df)
    for row in df.itertuples():
        start = time.time()

        df = create_valid_themes_column(row, df)
        df = encode_fen(row, df)

        end = time.time()
        duration = end - start
        print("row time: %.4fs" % duration)

    themes_dummies = df.valid_themes.str.get_dummies(' ').add_prefix('theme_')
    df = pd.concat([df, themes_dummies], axis=1)

    df.drop(['Moves'], inplace=True, axis=1)
    df.drop(['Themes', 'valid_themes'], inplace=True, axis=1)
    df.drop(['FEN'], inplace=True, axis=1)
    df.to_csv(f'cleaned_puzzle_batches/cleaned_validation_batch.csv')


def create_valid_themes_column(row, df):
    row_themes = set(row.Themes.split())
    valid_themes = row_themes.intersection(USED_THEMES)
    df.at[row.Index, 'valid_themes'] = " ".join(valid_themes)

    return df


def create_board_positions_with_piece_vectors(df):
    squares = chess.SQUARE_NAMES

    # pawn, knight, bishop, rook, king
    # queen will be encoded as bishop + rook
    pieces = ['p', 'n', 'b', 'r', 'k'] 
    for s in squares:
        for p in pieces:
            df[f"{s}.{p}"] = 0

    return df


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
