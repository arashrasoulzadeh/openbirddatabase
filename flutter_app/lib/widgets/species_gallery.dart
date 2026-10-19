import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:openbird/models/species.dart';

/// The species photos (swipe to change) with the photographer's credit and licence under them.
class SpeciesGallery extends StatefulWidget {
  final List<SpeciesPhoto> photos;
  final String apiBaseUrl;
  final String creditLabel; // "Photo"

  const SpeciesGallery({
    super.key,
    required this.photos,
    required this.apiBaseUrl,
    required this.creditLabel,
  });

  @override
  State<SpeciesGallery> createState() => _SpeciesGalleryState();
}

class _SpeciesGalleryState extends State<SpeciesGallery> {
  final PageController _controller = PageController();
  int _index = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _open(String url) async {
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      // no app can open it: nothing to do
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.photos.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    final photo = widget.photos[_index.clamp(0, widget.photos.length - 1)];

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: SizedBox(
              height: 240,
              child: Stack(
                children: [
                  PageView.builder(
                    controller: _controller,
                    itemCount: widget.photos.length,
                    onPageChanged: (i) => setState(() => _index = i),
                    itemBuilder: (context, i) => Image.network(
                      widget.photos[i].url(widget.apiBaseUrl),
                      fit: BoxFit.cover,
                      width: double.infinity,
                      loadingBuilder: (context, child, progress) =>
                          progress == null ? child : const Center(child: CircularProgressIndicator()),
                      errorBuilder: (context, error, stack) =>
                          const Center(child: Icon(Icons.image_not_supported_outlined, size: 40)),
                    ),
                  ),
                  if (widget.photos.length > 1)
                    Positioned(
                      left: 0,
                      right: 0,
                      bottom: 8,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          for (var i = 0; i < widget.photos.length; i++)
                            Container(
                              width: 7,
                              height: 7,
                              margin: const EdgeInsets.symmetric(horizontal: 3),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: i == _index ? Colors.white : Colors.white54,
                              ),
                            ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 6),
          Wrap(
            spacing: 6,
            children: [
              Text(
                '${widget.creditLabel}: ${photo.author ?? '—'}',
                style: theme.textTheme.bodySmall,
              ),
              if (photo.license != null)
                InkWell(
                  onTap: () => _open(photo.licenseUrl),
                  child: Text('· ${photo.license}', style: theme.textTheme.bodySmall?.copyWith(decoration: TextDecoration.underline)),
                ),
              if (photo.page != null && photo.page!.isNotEmpty)
                InkWell(
                  onTap: () => _open(photo.page!),
                  child: Text('· ${photo.source ?? 'source'}', style: theme.textTheme.bodySmall?.copyWith(decoration: TextDecoration.underline)),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
