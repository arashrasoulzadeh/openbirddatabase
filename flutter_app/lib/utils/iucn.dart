import 'package:openbird/l10n/app_localizations.dart';

/// "EN" -> "Endangered" in the app's language; unknown codes are returned unchanged.
String iucnLabelFor(AppLocalizations l10n, String code) {
  switch (code) {
    case 'LC': return l10n.iucnLC;
    case 'NT': return l10n.iucnNT;
    case 'VU': return l10n.iucnVU;
    case 'EN': return l10n.iucnEN;
    case 'CR': return l10n.iucnCR;
    case 'EW': return l10n.iucnEW;
    case 'EX': return l10n.iucnEX;
    case 'DD': return l10n.iucnDD;
    default: return code;
  }
}
