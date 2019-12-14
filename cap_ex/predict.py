""" 이 모듈은 훈련된 신경 네트워크를 사용하여 미디 파일에 대한 노트를 생성 """
import pickle
import numpy
from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation

def generate():
    """ 미디 파일 생성 """

    # 모델을 훈련시키는데 사용한 노트 로드
    with open('data/notes', 'rb') as filepath:
        notes = pickle.load(filepath)

    # 음높이의 이름들을 다 가져옴
    pitchnames = sorted(set(item for item in notes))
    # 음높이 의 양
    n_vocab = len(set(notes))

    network_input, normalized_input = prepare_sequences(notes, pitchnames, n_vocab)
    model = create_network(normalized_input, n_vocab)
    prediction_output = generate_notes(model, network_input, pitchnames, n_vocab)
    create_midi(prediction_output)

def prepare_sequences(notes, pitchnames, n_vocab):
    """ 시퀀스 준비 """
    """ 문자열 데이터를 숫자 형식으로 나타내는 일을 진행
        이렇게 하는 이유는 문자열 기반 데이터보다 숫자 기반 데이터를 신경망이 더 잘 학습하기 때문 """

    # 음높이와 정수를 매핑하기 위한 dict
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    #이전 100개의 노트를 사용하여 예측
    sequence_length = 100
    network_input = []
    output = []
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # 입력 내용을 LSTM 계층과 호환되는 형식으로 다시 작성
    normalized_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # 정규화
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)

def create_network(network_input, n_vocab):
    """ 신경망의 구조 생성 """
    """ use Keras API """
    #LSTM : RNN 계층의 한 유형입니다.
    #Dropout : 정규화 기술. 이는 일부 노드를 임의로 삭제하여 모델이 과적 합되는 것을 방지합니다.
    #Dense : 이것은 모든 입력 노드가 모든 출력 노드에 연결되는 완전히 연결된 레이어입니다.
    #Activation : 노드의 출력을 생성하는 데 사용할 활성화 기능을 결정합니다.
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        return_sequences=True
    ))
    model.add(Dropout(0.2))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(512))
    model.add(Dense(256))
    model.add(Dropout(0.2))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    # 가중치 load
    model.load_weights('weights.hdf5')

    return model

def generate_notes(model, network_input, pitchnames, n_vocab):
    """ 노트를 기반으로 신경망에서 노트를 생성 """
    # 예측의 출발점, 입력에서 임의의 순서를 선택
    start = numpy.random.randint(0, len(network_input)-1)

    # 숫자를 문자로 매핑하기 위한 dict
    int_to_note = dict((number, note) for number, note in enumerate(pitchnames))

    pattern = network_input[start]
    prediction_output = []

    # 500개 노트 생성 (약 2분)
    for note_index in range(500):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        #입력 값에 대해 다음 노트를 예측
        prediction = model.predict(prediction_input, verbose=0)
        #네트워크 출력에서 가장 가능성이 높은 예측값을 결정하기 위해 가장 높은 확률의 인덱스를 추출
        index = numpy.argmax(prediction)

        result = int_to_note[index]
        prediction_output.append(result)
        pattern.append(index)
        pattern = pattern[1:len(pattern)]

    return prediction_output

def create_midi(prediction_output):
    """ 예측에서 노트로 출력을 변환하고 노트에서 미디 파일을 생성 """

    """ 패턴이 코드(chord) 인 경우 문자열을 여러 노트로 분할, 각 노트의 문자열 표현을 반복하여 각 노트에 대한 노트 개체를 생성
        => 각 노트를 포함하는 코드(chord) 개체 생성 가능
        
        패턴이 노트 인 경우 패턴에 포함된 계이름을 표현하는 문자열 표현을 사용하여 노트 개체를 생성 """

    offset = 0
    output_notes = []

    # 모델에 의해 생성된 값을 기반으로 노트 및 코드 객체 작성
    for pattern in prediction_output:
        # 패턴이 chord 일 경우
        # 코드(chord)는 동시에 연주되는 노트 세트를 위한 컨테이너
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                #피아노로 출력
                new_note.storedInstrument = instrument.Horn()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        # 패턴이 note 일 경우
        # 노트에는 노트의 계이름, 옥타브 및 오프셋
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Horn()
            output_notes.append(new_note)

        # 같은 오프셋에 음이 쌓이기 때문에 각 반복마다 오프셋을 0.5씩 증가
        offset += 0.5

    midi_stream = stream.Stream(output_notes)

    midi_stream.write('midi', fp='test_output.mid')

if __name__ == '__main__':
    generate()
