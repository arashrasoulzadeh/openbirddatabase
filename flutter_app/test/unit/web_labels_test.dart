import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/utils/countries.dart';
import 'package:openbird/utils/web_labels.dart';

void main() {
  test('values and fields are translated like on the website, with English as the fallback', () {
    expect(valueLabelFor('en', 'Forest'), 'Forest');
    expect(valueLabelFor('fa', 'Forest'), isNot('Forest'));
    expect(valueLabelFor('fa', 'Not in the list'), 'Not in the list');
    expect(fieldLabelFor('en', 'body_mass_g'), isNotEmpty);
    expect(fieldLabelFor('de', 'body_mass_g'), isNotEmpty);
    expect(fieldLabelFor('en', 'some_unknown_field'), 'Some unknown field');
  });

  test('country codes become flag emoji, anything else is left alone', () {
    expect(flagEmoji('FR'), '\u{1F1EB}\u{1F1F7}');
    expect(flagEmoji('de'), '\u{1F1E9}\u{1F1EA}');
    expect(flagEmoji('X1'), 'X1');
    expect(flagEmoji('FRA'), 'FRA');
  });
}
