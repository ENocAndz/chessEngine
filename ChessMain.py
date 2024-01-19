# Main driver filee. Handles user input
import pygame as p 
import ChessEngine, smartMoveFinder


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = BOARD_WIDTH / 2
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT

DIMENSION = 8  # chessboard 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
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
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont =p.font.SysFont("Arial", 15, False,False)
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
    playerTwo = True 
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
                    if sqSelected == (row,col) or col >= 8: 
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
        drawGameState(screen,gs,validMoves,sqSelected, moveLogFont)
        
        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Stalemate" if gs.stalemate else "Black wins by Checkmate" if gs.whiteToMove else  "White wins by Checkmate"
            drawEndGameText(screen,text)
        
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs,validMoves,sqSelected,moveLogFont):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color(154,250,154)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        
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
                        

            
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"),moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range (0, len(moveLog),2):
        moveString = str(i// 2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "      "
        moveTexts.append(moveString )
    movesPerRow = 2
    padding = 5
    textY = padding
    lineSpacing = 2
    for i in range(0,len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text,0,p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject,textLocation)
        textY += textObject.get_height() + lineSpacing
    
                
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
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1 ) if move.pieceCaptured[0] == 'b' else move.endRow -1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
            
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)
        
        
def drawEndGameText(screen,text):
    font = p.font.SysFont("Helvetica", 32, True,False)
    textObject = font.render(text,0,p.Color('Black'))
    textLocation = p.Rect(0,0, BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2,BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0 , p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))
    

if __name__ == "__main__":
    main()
    