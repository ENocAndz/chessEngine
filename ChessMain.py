# Main driver filee. Handles user input
import pygame as p 
import ChessEngine, smartMoveFinder


WIDTH = HEIGHT = 512
DIMENSION = 8  # chessboard 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 
IMAGES = {}

def loadImages():
    pieces = ["wR","wN","wB","wQ","wK","wp","bR","bN","bB","bQ","bK", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))
        
        
'''
main for handling input and updating graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # move has been Made flag
    animate = False #Flag
    loadImages()
    running = True
    sqSelected = ()#tuple row,col
    playerClicks = [] # two tuples: row,col  
    gameOver = False
    playerOne = True #if human playing white then true, if ai playing then false
    playerTwo = False 
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo )
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: #moving pieces with mouse
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): 
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = [] 
                                print(move.getChessNotation())
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    gameOver = False
                    moveMade = False
                    animate = False
                    
                
                
        # ai movefinder
        if not gameOver and not humanTurn:
            print("hello")
            AIMove = smartMoveFinder.findBestMove(gs,validMoves)
            if AIMove is None:
                AIMove = smartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
            
        
        if moveMade:
            if animate:
                animateMoves(gs.moveLog[-1],screen,gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen,gs,validMoves,sqSelected)
        
        if gs.checkmate:
            print("checkmate")
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen,"white wins by Checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')
        
        clock.tick(MAX_FPS)
        p.display.flip()
        
#Highlight squares
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w'if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha()
            s.fill(p.Color(115,148,115))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color(194,56,41))
            circle_surface = p.Surface((int(SQ_SIZE / 2), int(SQ_SIZE / 2)), p.SRCALPHA)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if  gs.board[move.endRow][move.endCol] == '--':                     
                        center_x = int((move.endCol + 0.5) * SQ_SIZE)
                        center_y = int((move.endRow + 0.5) * SQ_SIZE)
                        
                        p.draw.circle(circle_surface, (115,148,115, 100), (int(SQ_SIZE / 4), int(SQ_SIZE / 4)), int(SQ_SIZE / 5), 0)
                    
                        screen.blit(circle_surface, (center_x - int(SQ_SIZE / 4), center_y - int(SQ_SIZE / 4)))
                    else:
                        screen.blit(s,(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
                        
                    
            
def drawGameState(screen, gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)
    
    
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color(154,250,154)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                
#Animating moves
def animateMoves(move,screen,board,clock):
    global colors
    coords =[] # coordinations from animation movement
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 9
    frameCount=(abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c =(move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase piece moved from ending Square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
            
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)
        
        
def drawText(screen,text):
    font = p.font.SysFont("Helvetica", 32, True,False)
    textObject = font.render(text,0,p.Color('Black'))
    textLocation = p.Rect(0,0, WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2,HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    

if __name__ == "__main__":
    main()
    