import argparse
import re
from bs4 import BeautifulSoup

TAG_REGEX = re.compile('<(.+?)\s')
CLASS_REGEX = re.compile('class=\"(.+?)\"')
TITLE_REGEX = re.compile('title=\"(.+?)\"')
HREF_REGEX = re.compile('href=\"(.+?)\"')
CONTENT_REGEX = re.compile('>\s*(.+)\s*</')
ID_REGEX = re.compile('id=\"(.+?)\"')


# The reasoning behind parameter weights is that element id must be more than
# anything else, and content (button text) should weigh more than anything else
# except the id
PARAMETER_WEIGHTS = {
    'id': 10,
    'content': 5,
    'tag': 1,
    'class': 1,
    'title': 1,
    'href': 1,
}


def exit_with_an_error(message):
    print(message)
    exit()


def read_file(path):
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        exit_with_an_error('File not found')
    return content


def get_element_by_id(html, id):
    soup = BeautifulSoup(html, 'html.parser')
    element = soup.find(id=id)

    if not element:
        exit_with_an_error('No element with the given ID found')

    return element


def search_elements_by_tag(html, tag):
    if not tag:
        exit_with_an_error('No original element tag is known')

    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all(tag)

    return elements


# creates element path strings
def get_element_path(element, path):
        parent = element.parent
        if parent:
            name = parent.name
            attrs = parent.attrs
            if 'class' in attrs.keys():
                for attribute in attrs['class']:
                    name = '{}.{}'.format(name, attribute)
            if 'id' in attrs.keys():
                name = '{}#{}'.format(name, attrs['id'])
            path = '{} > {}'.format(name, path)
            path = get_element_path(parent, path)
        return path


# parses element attributes, by which we then determine if this is the element we search for
def parse_element(element, index=0):
    el_id = ID_REGEX.search(element)
    el_tag = TAG_REGEX.search(element)
    el_class = CLASS_REGEX.search(element)
    el_title = TITLE_REGEX.search(element)
    el_href = HREF_REGEX.search(element)
    el_content = CONTENT_REGEX.search(element)

    element_characteristics = {
        'id': el_id and el_id.group(1) or None,
        'tag': el_tag and el_tag.group(1) or None,
        'class': el_class and el_class.group(1) or None,
        'title': el_title and el_title.group(1) or None,
        'href': el_href and el_href.group(1) or None,
        'content': el_content and el_content.group(1) or None,
        'index': index
    }

    return element_characteristics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('origin_file_path', type=str, help='Origin file path')
    parser.add_argument('diff_file_path', type=str, help='Diff file path')
    args = parser.parse_args()

    origin = read_file(args.origin_file_path)
    diff = read_file(args.diff_file_path)
    original_element = get_element_by_id(origin, "make-everything-ok-button")
    parsed_original = parse_element(str(original_element))
    candidate_elements = search_elements_by_tag(diff, parsed_original.get('tag'))
    candidates_parsed = [parse_element(str(el), idx) for idx, el in enumerate(candidate_elements)]

    # in order to find the best match we compare original element attributes
    # with the attributes of candidate elements and add weight points for
    # every identical attribute
    elements_by_weight = {}
    for el in candidates_parsed:
        weight = 0
        print('Candidate element: {}'.format(el))
        for key, value in el.items():
            if key not in ('index', 'tag') and value == parsed_original[key]:
                print('"{}" parameter is identical, candidate weight is increased by {}'
                      .format(key, PARAMETER_WEIGHTS[key]))
                weight += PARAMETER_WEIGHTS[key]
        elements_by_weight[weight] = el

    max_weight = max(elements_by_weight.keys())
    element_found = elements_by_weight[max_weight]
    element = candidate_elements[element_found['index']]
    parsed = parse_element(str(element))
    element_name = parsed['tag']
    if parsed['id']:
        element_name = '{}#{}'.format(element_name, parsed['id'])
    if parsed['class']:
        element_name = '{}.{}'.format(element_name, parsed['class'])
    element_path = get_element_path(element, element_name)
    print('Biggest element weight: {}'.format(max_weight))
    print('Found element: {}'.format(element_path))


if __name__ == '__main__':
    main()
