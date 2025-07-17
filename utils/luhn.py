def luhnify(number: str) -> str:
    def luhn_checksum(card_number):
        def digits_of(n): return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    if not number.isdigit():
        number = ''.join(filter(str.isdigit, number))

    checksum = luhn_checksum(number + '0')
    check_digit = (10 - checksum) % 10
    return number + str(check_digit)
