sen=input()#입력받기
sen_SP = sen.split(' ')#각 값들을 띄어쓰기에 맞춰 리스트 sen_SP에 입력
print("="*50)
print("결과")
print("="*50)

def isNumber(sen):#입력받은 값이 숫자인지 확인하는 함수
  try:
    float(sen)
    return True
  except ValueError:
    return False

def swap(x, i, j):#두 값의 위치를 바꾸는 함수
    x[i], x[j] = x[j], x[i]

def Pivot(x, Left, Right):#퀵소팅을 위한 함수
    pivot_val = x[Left]
    pivot_idx = Left
    while Left <= Right:
        while Left <= Right and x[Left] <= pivot_val:
            Left += 1
        while Left <= Right and x[Right] >= pivot_val:
            Right -= 1
        if Left <= Right:
            swap(x, Left, Right)
            Left += 1
            Right -= 1
    swap(x, pivot_idx, Right)
    return Right

def quickSort(x):#Pivot함수를 이용해 퀵소팅을 하는 함수
    def q_sort(x, first, last):#퀵소팅 반복
        if first < last:
            splitpoint = Pivot(x, first, last)
            q_sort(x, first, splitpoint-1)
            q_sort(x, splitpoint+1, last)
    q_sort(x, 0, len(x)-1)

if sen_SP[0]!='-o':#예외 처리1
    print("구문 오류 : 001\n-o가 생략되었습니다")
elif (sen_SP[1] != 'A' and sen_SP[1] != 'D'):#예외 처리2
    print("구문 오류 : 002\n오름차순은 A 내림차순은 D를 입력해야 합니다")
elif sen_SP[2] != '-i':#예외 처리3
    print("구문 오류 : 003\n숫자 입력시 앞서 -i를 입력해야 합니다")
else:
    ty=' '
    if sen_SP[1] == 'A':#정렬 타입지정
        ty='A'
    else:
        ty='D'
    del sen_SP[0]#처음 -o AorD -i를 삭제
    del sen_SP[0]
    del sen_SP[0]
    k = 0#예외처리 4를 확인하기 위한 변수

    for i in sen_SP:#예외 처리4
        if(isNumber(i) == False):
            print("구문 오류 : 004\n배열의 값은 숫자만 가능합니다")
            k = k+1
            break
    if (ty == 'A' and k == 0 ):
        sen_SP = [int (i) for i in sen_SP]#모든 값을 문자열에서 숫자로 변환
        quickSort(sen_SP)#퀵소팅
        print(sen_SP)#결과를 출력
    elif (ty =='D' and k == 0):
        sen_SP = [int (i) for i in sen_SP]
        quickSort(sen_SP)
        sen_SP.reverse()#리스트의 순서를 반전시킴
        print(sen_SP)