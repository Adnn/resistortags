#!/usr/bin/env python3

import argparse

import jinja2


class Resistance(object):
    def __init__(self, value):
        self.digits = [digit for digit in str(value)]

    def __str__(self):
        return str("{}.{}".format(self.digits[0],
                                  ''.join(self.digits[1:])))

    def cms(self, decade):
        if decade == -2:
            raise Exception("To be implemented: don't know how that works")
        elif decade == -1:
            return  "R{}".format(''.join(self.digits))
        else:
            return "{}{}".format(''.join(self.digits), decade)


    def text_value(self, decade):
        value = round(float(''.join(self.digits)) * pow(10, decade), 2)
        if value >= pow(10, 6):
            return "{0:g}M".format(value / pow(10, 6))
        elif value >= pow(10, 3):
            return "{0:g}k".format(value / pow(10, 3))
        else:
            return "{0:g}".format(value)


    def template_parameter(self, decade):
        return {
            "text": self.text_value(decade),
            "cms": self.cms(decade),
            "decade": decade,
            "digits": self.digits,
        }


def serie_gen(n):
    # E24 has some values diverging from the computation.
    # see: https://en.wikipedia.org/wiki/E_series_of_preferred_numbers
    if n == 24:
        for value in (10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91):
            yield Resistance(value);

    else:
        factor = 10 if n <= 12 else 100;
        for m in range(n):
            yield Resistance(round(pow(pow(10, m), 1/float(n)) * factor))


def get_template():
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    return templateEnv.get_template("tag_template.html")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Generates a web page containing a collection of resistor tags.")
    parser.add_argument("serie", type=int, choices=[3, 6, 12, 24, 48, 96, 192], help="The series (24 corresponds to E24)")
    parser.add_argument("decadelow", type=int, choices=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                             help="The decade, expressed as the corresopnding power of 10. (e.g. -1 for gold, which is factor 0.1)")
    parser.add_argument("decadehigh", type=int, choices=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                             help="The decade, expressed as the corresopnding power of 10. (e.g. -1 for gold, which is factor 0.1)")

    args = parser.parse_args()
    if args.decadehigh < args.decadelow:
        raise Exception("'decadehigh' value must be >= to 'decadelow' value.")

    resistors = [r.template_parameter(decade)
                    for decade in range(args.decadelow, args.decadehigh+1)
                        for r in serie_gen(args.serie)]

    template = get_template()
    with open("tag_render.html", "w") as destination:
        destination.write(template.render({"resistors": resistors}))
