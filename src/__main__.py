from .parser import Parser


def main():
    parser = Parser()

    print(
        parser.args.func_def_file,
        parser.args.input_file,
        parser.args.output_file,
        sep='\n'
    )


if __name__ == '__main__':
#    try:
    main()
#    except BaseException as e:
#        print(e)
