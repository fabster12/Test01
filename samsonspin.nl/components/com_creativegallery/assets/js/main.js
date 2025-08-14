(function ($) {
    $(document).ready(function() {
        $('div.creative-gallery-container').each(function (index, el) {
            var id = 'creative-gallery-' + index;
            $(el).attr('id', id);
            var options = $(el).data();
            options.elementID = id;

            var gallery = new CreativeGallery(options);
        });
    });
})(creativeSolutionsjQuery);
