""" 이 모듈은 미디 파일 데이터를 준비하여 훈련을 위해 신경 네트워크에 공급 """
import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint

def train_network():
    """ 음악을 생성하기 위해 신경망 훈련 """

    notes = get_notes()

    # 음높이 의 양
    n_vocab = len(set(notes))

    # 노트를 숫자 입력으로 변환
    network_input, network_output = prepare_sequences(notes, n_vocab)

    # 신경망 구조 생성
    model = create_network(network_input, n_vocab)

    train(model, network_input, network_output)

def get_notes():
    """ ./midi_songs 디렉토리의 midi 파일에서 모든 노트 및 코드 가져오기 """

    notes = []

    for file in glob.glob("midi_songs/*.mid"):
        midi = converter.parse(file)

        print("Parsing %s" % file)

        notes_to_parse = None

        try: #  악기 부분
            s2 = instrument.partitionByInstrument(midi)
            notes_to_parse = s2.parts[0].recurse() 
        except: # flat 부분
            notes_to_parse = midi.flat.notes

        for element in notes_to_parse:
            # Note일 경우
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            # Chord일 경우
            elif isinstance(element, chord.Chord):
                notes.append('.'.join(str(n) for n in element.normalOrder))

    # 자료형을 파일로 저장
    with open('data/notes', 'wb') as filepath:
        pickle.dump(notes, filepath)

    return notes

def prepare_sequences(notes, n_vocab):
    """ 신경망에서 사용하는 시퀀스 준비 """

    sequence_length = 100

    # 음높이 이름을 가져옴
    pitchnames = sorted(set(item for item in notes))

    # 음높이와 정수를 매핑하기 위한 dict
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    network_input = []
    network_output = []

    # 입력 시퀀스 및 해당 출력 생성
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        network_output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # 입력 내용을 LSTM 계층과 호환되는 형식으로 다시 작성
    network_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # 정규화
    network_input = network_input / float(n_vocab)
    # one-hot 인코딩
    network_output = np_utils.to_categorical(network_output)

    return (network_input, network_output)

def create_network(network_input, n_vocab):
    """ 신경망의 구조 생성, Keras API 활용"""
    # LSTM : RNN 계층의 한 유형입니다.
    # Dropout : 정규화 기술. 이는 일부 노드를 임의로 삭제하여 모델이 과적 합되는 것을 방지합니다.
    # Dense : 이것은 모든 입력 노드가 모든 출력 노드에 연결되는 완전히 연결된 레이어입니다.
    # Activation : 노드의 출력을 생성하는 데 사용할 활성화 기능을 결정합니다.
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
    # 결과를 확률값으로 해석하기 위해 활성함수로 softmax 사용
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    return model

def train(model, network_input, network_output):
    """ 신경망 훈련, Checkpoint 생성, Keras fit 이용 """

    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    # verbose = 해당 함수의 진행 사항의 출력 여부 옵션
    # save_best_only = 모델의 정확도가 최고값을 갱신했을 때만 저장하도록 하는 옵션
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    model.fit(network_input, network_output, epochs=200, batch_size=32, callbacks=callbacks_list)

if __name__ == '__main__':
    train_network()
