const letters = [...'abcdefghijklmnopqrstuvwxyz0123456789']
const dfl = [
    '000001', // a/A
    '000010', // b/B
    '000100', // c/C
    '001000', // d/D
    '000011', // e/E
    '000110', // f/F
    '001100', // g/G
    '000111', // h/H
    '001110', // i/I
    '001001', // j/J
    '001010', // k/K
    '001100', // l/L
    '001011', // m/M
    '001110', // n/N
    '001101', // o/O
    '000101', // p/P
    '010001', // q/Q
    '010010', // r/R
    '010100', // s/S
    '011000', // t/T
    '011001', // u/U
    '011010', // v/V
    '011100', // w/W
    '011101', // x/X
    '010011', // y/Y
    '011111', // z/Z
    '100001', // 0
    '100010', // 1
    '100100', // 2
    '101000', // 3
    '110000', // 4
    '100011', // 5
    '100110', // 6
    '101100', // 7
    '111000', // 8
    '100111'  // 9
];

const translateToDFL = (text) => {
    let inputValue = text.replace(/\s/g, '').slice(0, 10);
    if (inputValue == ""){
        return
    }

    let words = inputValue.split("");
    let result = []

    for (let letter of words){
        if (letter == " "){ continue; }
        let idx = letters.indexOf(letter.toLowerCase())

        if (idx == -1){
            result.push(letter)
            continue
        }

        result.push(dfl[idx]);
    }

    return result.join(" ")
}
