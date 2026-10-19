/// ISO 3166 alpha-2 code -> flag emoji ("FR" -> 🇫🇷). Works in every language; anything unexpected is returned as is.
String flagEmoji(String code) {
  final c = code.trim().toUpperCase();
  if (c.length != 2 || c.codeUnits.any((u) => u < 0x41 || u > 0x5A)) return code;
  return String.fromCharCodes(c.codeUnits.map((u) => 0x1F1E6 + u - 0x41));
}
