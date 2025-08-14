(function ($) {
	window.CreativeGallery = function (options) {

		this.options = options;

		this.options.imageLoadingTimeout = options.imageLoadingTimeout || 10000;
		this.options.imageLazyLoadingTimeout = options.imageLazyLoadingTimeout || 5000;
		this.options.imageLoadStatusCheck = options.imageLoadStatusCheck || 30;

		this.element = $('div#' + options.elementID);
		this.tags = this.element.find('div.cg_tags');
		this.gallery = this.element.find('ul.gallery');

		this.currentPage = 1;

		this.previewCoverTimeout = '';

		this.element.find('div.preview-timer-inner').css('transition', 'all ' + this.options.prev_speed+ 's linear');

		// If Ajax Request is not working

		this.init = function() {
			/// TODO Make BackEnd Options for all parameters
			this.lightbox = new CreativeLightbox({
				outputDirectory: null,
				transitionDelay: null,
				minTopValue: null,
				minLeftValue: null,
				thumbnailWidth: this.options.lightbox_thumbnail_width,
				thumbnailHeight: this.options.lightbox_thumbnail_height,
				captionEnabled: this.options.lightbox_caption_enebled,
				captionHeight: this.options.lightbox_caption_height,
				imageLoadingTimeout: this.options.lightbox_image_loading_timeout,
				imageLoadStatusCheck: null,
				carouselImagesMargin: this.options.lightbox_carousel_images_margin,
				mapSize: this.options.lightbox_carousel_map_size,
				mapIconsMaxVisible: this.options.lightbox_carousel_map_icons_max_visible,
				carouselMode: this.options.lightbox_type,
				autoplay: this.options.lightbox_autoplay_enebled,
				slideSpeed: this.options.lightbox_carousel_slide_speed
			});

			this.calculatePossitions();
			this.gallery.find('li').each(function (index, el) {
				var currentElement = $(el).find('img');
				this.prepareThumbnails(currentElement);
			}.bind(this));

			this.initTags();
			this.attachEvents();

			if (this.options.hover === 14) {
				var directionAware = new DirectionAwareHover({
					wrapper: this.element
				});
			}

		}.bind(this);

		this.initPages = function () {
			var pagesWrapper = this.element.find("div.cg_pages");

			var visibleImagesCount = this.element.find('li.visible').length;

			pagesWrapper.find('span').remove('*');

			totalPagesCount = Math.floor(visibleImagesCount/(this.options.max_image_per_page*1))+1;

			for (var i = 1; i <= totalPagesCount; i++) {
				var span = document.createElement('span');
				span.innerHTML = i;
				span.className = 'creative-gallery-tag';
				if (this.currentPage === i) {
					span.className += ' selected';
				}
				pagesWrapper.append(span);
			}
		}.bind(this);
		this.calculatePossitions = function () {
			var containerW = this.gallery.width()*1;
			var thumbnailMargin = this.options.margin*1;
			var thumbnailSize = this.options.size*1;
			var thumbnailBorder = this.options.img_border_width*1;

			var currentPageIndexMin = (this.currentPage-1)*this.options.max_image_per_page;
			var currentPageIndexMax = this.currentPage*this.options.max_image_per_page;

			var calculatedMargin;
			var extraClass;
			switch (this.options.view) {
				case 1:
					var count = Math.floor((containerW+thumbnailMargin)/(thumbnailSize+thumbnailMargin+thumbnailBorder*2)),
						leftMargin = Math.round((containerW - count*(thumbnailSize+thumbnailBorder*2) - (count-1)*(thumbnailMargin))/2),
						currentX = leftMargin,
						currentY = 0,
						counter = 1;
					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth = thumbnailSize,
							currentHeight = thumbnailSize;
						if (index>=currentPageIndexMin && index<currentPageIndexMax) {
							$(el).removeClass('next-page').css({
								width: currentWidth + "px",
								height: currentHeight + "px",
								top: currentY + "px",
								left: currentX + "px"
							}).attr({
								'data-index': index
							});
							if (counter%count==0) {
								currentX = leftMargin;
								currentY = currentY + currentHeight + thumbnailMargin + thumbnailBorder*2;
							} else {
								currentX = currentX + currentWidth + thumbnailMargin + thumbnailBorder*2;
							}
							counter ++;
						} else {
							$(el).addClass('next-page');
						}
					}.bind(this));

					if (currentX==leftMargin) {
						this.gallery.height(currentY);
					} else {
						this.gallery.height(currentY + thumbnailMargin + thumbnailBorder + thumbnailSize);
					}
				break;
				case 2:
					var count = Math.floor((containerW+thumbnailMargin)/(thumbnailSize+thumbnailMargin+thumbnailBorder*2)),
						leftMargin = Math.round((containerW - count*(thumbnailSize+thumbnailBorder*2) - (count-1)*(thumbnailMargin))/2),
						currentX = [],
						currentY = [];
						currentX[currentPageIndexMin] = leftMargin;
					for (var i = currentPageIndexMin; i < currentPageIndexMax; i++) {
						currentY[i] = 0;
					}


					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if ($(el).attr('data-loaded')) {
							currentWidth = $(el).find('img')[0].naturalWidth;
							currentHeight = $(el).find('img')[0].naturalHeight;
						} else {
							currentWidth = thumbnailSize;
							currentHeight = thumbnailSize;
						}

						if (index>=currentPageIndexMin && index<currentPageIndexMax) {
							$(el).addClass('notransition');
							$(el)[0].offsetWidth;
							$(el).removeClass('next-page').css({
								width: currentWidth + "px",
								height: currentHeight + "px",
								top: currentY[index] + "px",
								left: currentX[index] + "px"
							}).attr({
								'data-index': index
							});
							if ((index+1)%count==0) {
								currentX[index+1] = leftMargin;
							} else {
								currentX[index+1] = currentX[index] + currentWidth + thumbnailMargin + thumbnailBorder*2;
							}
							currentY[index+count] = currentY[index] + currentHeight + thumbnailMargin + thumbnailBorder*2;
							$(el).removeClass('notransition');
						} else {
							$(el).addClass('next-page');
						}
					}.bind(this));
					currentY.sort(function (a, b) {
						return b-a;
					});
					this.gallery.height(currentY[0]);
					break;
				case 3:
					var count = Math.floor((containerW+thumbnailMargin)/(thumbnailSize+thumbnailMargin+thumbnailBorder*2)),
						leftMargin = Math.round((containerW - count*(thumbnailSize+thumbnailBorder*2) - (count-1)*(thumbnailMargin))/2),
						currentX = [],
						currentY = [],
						widthPerRow = [],
						row = 0;
						widthPerRow[row] = 0;
					currentX[currentPageIndexMin] = leftMargin;
					for (var i = currentPageIndexMin; i < currentPageIndexMax; i++) {
						currentY[i] = 0;
					}


					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if ($(el).attr('data-loaded')) {
							currentWidth = $(el).find('img')[0].naturalWidth;
							currentHeight = $(el).find('img')[0].naturalHeight;
						} else {
							currentWidth = thumbnailSize;
							currentHeight = thumbnailSize;
						}
						if (index>=currentPageIndexMin && index<currentPageIndexMax) {
							$(el)[0].offsetWidth;
							$(el).addClass('notransition');

							$(el).removeClass('next-page').css({
								width: currentWidth + "px",
								height: currentHeight + "px",
								top: currentY[index] + "px",
								left: currentX[index] + "px"
							}).attr({
								'data-index': index
							});
							if ((index+1)%count==0) {
								currentX[index+1] = leftMargin;
								widthPerRow[row] = widthPerRow[row] + currentWidth;
								row ++;
								widthPerRow[row] = 0;
							} else {
								currentX[index+1] = currentX[index] + currentWidth + thumbnailMargin + thumbnailBorder*2;
								widthPerRow[row] = widthPerRow[row] + currentWidth;
							}
							currentY[index+count] = currentY[index] + currentHeight + thumbnailMargin + thumbnailBorder*2;
						} else {
							$(el).addClass('next-page');
						}

					}.bind(this));
					row = 0;
					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if ($(el).attr('data-loaded')) {
							currentWidth = $(el).find('img')[0].naturalWidth*1;
							currentHeight = $(el).find('img')[0].naturalHeight*1;
						} else {
							currentWidth = thumbnailSize*1;
							currentHeight = thumbnailSize*1;
						}
						if (index>=currentPageIndexMin && index<currentPageIndexMax) {

							var widthDifference = (widthPerRow[row]-count*thumbnailSize)/(count*thumbnailSize);
							if (widthDifference > 0) {
								currentWidth = currentWidth - thumbnailSize*widthDifference;
							}
							$(el).css({
								width: currentWidth + "px",
								left: currentX[index] + "px"
							});
							$(el).find('img').addClass('notransition');
							$(el).find('img').addClass('transform-center-x');
							$(el).find('img')[0].offsetWidth;
							$(el).find('img').removeClass('notransition');
							if ((index+1)%count==0) {
								currentX[index+1] = leftMargin;
								row ++;
							} else {
								currentX[index+1] = currentX[index] + currentWidth + thumbnailMargin + thumbnailBorder*2;
							}
							currentY[index+count] = currentY[index] + currentHeight + thumbnailMargin + thumbnailBorder*2;
							$(el).removeClass('notransition');
						} else {
							$(el).addClass('next-page');
						}

					}.bind(this));
					currentY.sort(function (a, b) {
						return b-a;
					});
					this.gallery.height(currentY[0]);
					break;
				case 4:
					var currentX = 0,
						currentY = 0;
					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if ($(el).attr('data-loaded')) {
							currentWidth = $(el).find('img')[0].naturalWidth;
							currentHeight = $(el).find('img')[0].naturalHeight;
						} else {
							currentWidth = thumbnailSize;
							currentHeight = thumbnailSize;
						}
						$(el).addClass('notransition');
						$(el)[0].offsetWidth;
						$(el).css({
							width: currentWidth + "px",
							height: currentHeight + "px",
							top: currentY + "px",
							left: currentX + "px",
							cursor: 'pointer'
						}).attr({
							'data-index': index,
							'data-top' : currentY + "px",
							'data-left' : currentX + "px"
						});
						currentX = currentX + currentWidth + thumbnailMargin + thumbnailBorder*2;
						$(el).removeClass('notransition');
					}.bind(this));
					break;
				case 5:
					var currentX = 0,
						currentY = 0;
					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if ($(el).attr('data-loaded')) {
							currentWidth = $(el).find('img')[0].naturalWidth;
							currentHeight = $(el).find('img')[0].naturalHeight;
						} else {
							currentWidth = thumbnailSize;
							currentHeight = thumbnailSize;
						}
						$(el).addClass('notransition');
						$(el)[0].offsetWidth;
						$(el).css({
							width: currentWidth + "px",
							height: currentHeight + "px",
							top: currentY + "px",
							left: currentX + "px",
							cursor: 'pointer'
						}).attr({
							'data-index': index,
							'data-top' : currentY + "px",
							'data-left' : currentX + "px"
						});
						currentY = currentY + currentHeight + thumbnailMargin + thumbnailBorder*2;
						$(el).removeClass('notransition');
					}.bind(this));
					var seperator = this.element.find('.creative-gallery-seperator-vertical'),
						seperatorW = parseInt(seperator.css('borderLeftWidth')),
						seperatorMargin = parseInt(seperator.css('marginLeft'));
						this.element.find('.preview-container').width(this.element.width() - 2*thumbnailBorder - thumbnailSize - seperatorW - 2*seperatorMargin).css('float', 'left');
					break;
				case 6:
					var count = this.options.count,
						leftMargin = Math.round((containerW - count*(thumbnailSize+thumbnailBorder*2) - (count-1)*(thumbnailMargin))/2),
						currentX = leftMargin,
						currentY = 0,
						counter = 1;

						currentPageIndexMin = (this.currentPage-1)*count;
						currentPageIndexMax = this.currentPage*count;

					this.gallery.find('li.visible').each(function (index, el) {
						var currentWidth,
							currentHeight;
						if (index>=currentPageIndexMin && index<currentPageIndexMax) {
							if ($(el).removeClass('next-page').attr('data-loaded')) {
								currentWidth = $(el).find('img')[0].naturalWidth;
								currentHeight = $(el).find('img')[0].naturalHeight;
							} else {
								currentWidth = thumbnailSize;
								currentHeight = thumbnailSize;
							}
							$(el).css({
								width: currentWidth + "px",
								height: currentHeight + "px",
								top: currentY + "px",
								left: currentX + "px",
								cursor: 'pointer'
							}).attr({
								'data-index': index,
								'data-top' : currentY + "px",
								'data-left' : currentX + "px"
							});
							counter ++;
							if (counter > count) {
								currentX += 2*leftMargin + currentWidth + thumbnailMargin + thumbnailBorder*2;
								counter = 1;
							} else {
								currentX = currentX + currentWidth + thumbnailMargin + thumbnailBorder*2;
							}
						} else {
							$(el).addClass('next-page');
						}

					}.bind(this));
				case 7:
				case 8:
				case 9:
				case 10:
					if (this.options.view === 7) {
						calculatedMargin = thumbnailMargin + 'px ' + thumbnailMargin + 'px ' + thumbnailMargin + 'px ' + '0px';
						extraClass = 'left';
					} else if (this.options.view === 8) {
						calculatedMargin = thumbnailMargin + 'px '  + '0px ' + thumbnailMargin + 'px ' + thumbnailMargin + 'px';
						extraClass = 'right';
					} else if (this.options.view === 10) {
						extraClass = 'center';
						calculatedMargin = thumbnailMargin + 'px auto';
					}
					this.gallery.find('li.hidden').parents('.image-wrapper').hide();
					this.gallery.find('li.visible').each(function (index, el) {
						if (this.options.view === 9) {
							if (Math.random()>0.5) {
								calculatedMargin = thumbnailMargin + 'px ' + thumbnailMargin + 'px ' + thumbnailMargin + 'px ' + '0px';
								extraClass = 'left';
							} else {
								calculatedMargin = thumbnailMargin + 'px '  + '0px ' + thumbnailMargin + 'px ' + thumbnailMargin + 'px';
								extraClass = 'right';
							}
						}
						var currentWidth = thumbnailSize,
							currentHeight = thumbnailSize;
						if (index>=currentPageIndexMin && index<currentPageIndexMax) {
							$(el).parents('.image-wrapper').removeClass('next-page').show();
							$(el).addClass(extraClass).css({
								width: currentWidth + "px",
								height: currentHeight + "px",
								margin: calculatedMargin
							}).attr({
								'data-index': index
							});
						} else {
							$(el).parents('.image-wrapper').addClass('next-page');
						}
					}.bind(this));
					break;
				case 8:
				case 9:
				break;
			}
			this.initPages();
		}.bind(this);

		this.prepareThumbnails = function (el) {
			var ImageThumbnailReadyPromise = this.checkIfThumbnailReady(el);
			ImageThumbnailReadyPromise.then(
				function() {
					var imageLoadPromise = this.checkIfimageLoaded(ImageThumbnailReadyPromise.el, ImageThumbnailReadyPromise.el.attr('data-thumbnail'));
					imageLoadPromise.then(
						function() {
							this.showImage(imageLoadPromise.el);
						}.bind(this),
						function() {
							this.showImageLoadingError(imageLoadPromise.el);
						}.bind(this)
					);
				}.bind(this),
				function() {
					this.showImageLoadingError(el);
				}.bind(this)
			);
		}.bind(this);

		this.showImageLoadingError = function (el) {
			el.siblings('.cg-main-area-cover').find('div.cl-main-loading').hide();
			el.siblings('.cg-main-area-cover').find('div.cl-main-image-issue-hint').show();
			el.siblings('.cg-main-area-cover').find('div.cl-main-image-issue-hint')
				.find('div.main-image-refresh-icon').off('click').on('click', function (e) {
				var elem  = $(e.target).parents('div.creative-gallery-image-wrapper').find('img');
				elem.siblings('.cg-main-area-cover').find('div.cl-main-loading').show();
				elem.siblings('.cg-main-area-cover').find('div.cl-main-image-issue-hint').hide();
				this.prepareThumbnails(elem);
			}.bind(this));
		}.bind(this);

		this.initTags = function () {
			var tagsWrapper = this.element.find("div.cg_tags");
			tagsWrapper.on('click', 'span', function(event) {
				var tagIdList = Array();
				if (!event.ctrlKey) {
					$(event.target).addClass('selected').siblings('span').removeClass('selected');
				} else {
					$(event.target).addClass('selected');
				}
				tagsWrapper.find('span.selected').each(function(index, el) {
					tagIdList.push($(el).attr('data-id'));
				});
				this.element.find('li').each(function(index, el) {
					var tags = $(el).find("img").attr('data-tags'),
						tags_arr = tags.split(" ");

					if ($.inArray("-1", tagIdList)!=-1) {
						$(el).removeClass('hidden').removeClass('next-page').addClass('visible');
					} else {
						for (var i = 0; i < tagIdList.length; i++) {
							var tag_id = tagIdList[i];
							if ($.inArray(tag_id, tags_arr)!=-1) {
								$(el).removeClass('hidden').removeClass('next-page').addClass('visible');
								break;
							} else {
								$(el).removeClass('visible').addClass('hidden');
							}
						}
					}
				});
				this.currentPage = 1;
				this.calculatePossitions();
				if ((this.options.view === 4)||(this.options.view === 5)) {
					this.loadCurrentSlide(this.gallery.find('li.visible')[0]);
				}

			}.bind(this));
		}.bind(this);

		this.attachEvents = function () {
			$(window).on('resize', function () {
				this.calculatePossitions();
			}.bind(this));
			var filter_zoom = "";
			var filter_link = "";
			switch (this.options.img_icon_type) {
				case "both":
					filter_link = 'div.creative-gallery-icon-link';
				case "zoom_only":
					filter_zoom = "div.creative-gallery-icon-zoom";
					break;
				case "link_only":
					filter_link = 'div.creative-gallery-icon-link';
				case "none":
				default:
					filter_zoom = "img";
					this.element.find('li').css('cursor', 'pointer');
					break;
			}
			switch (this.options.view) {
				case 1:
				case 2:
				case 3:
				case 7:
				case 8:
				case 9:
				case 10:
					this.element.on('click', filter_zoom, function(event) {
						var startingIndex = $(event.target).parents('li.visible').attr('data-index');
						this.openPopup(startingIndex);
					}.bind(this));


					this.element.find('div.cg_pages').on('click', 'span', function(event) {
						this.element.find('div.cg_pages>span').removeClass('selected');
						this.currentPage = $(event.target).text()*1;
						$(event.target).addClass('selected');
						this.calculatePossitions();
					}.bind(this));

					if (filter_link === '') {
						return;
					}
					this.element.on('click', filter_link, function(event) {
						var link = $(event.target).parents('li').find('img').attr('data-link');
						var target = $(event.target).parents('li').find('img').attr('data-target');
						if (link!=='') {
							window.open(link, target==='1' ? '_blank' : '_self');
						}
					}.bind(this));
					break;
				case 4:
				case 5:
					this.loadCurrentSlide(this.gallery.find('li.visible')[0]);

					this.gallery.on('click', '.cl-carousel-prev-icon', function () {
						this.moveCarousel('prev', false);
					}.bind(this));

					this.gallery.on('click', '.cl-carousel-next-icon', function () {
						this.moveCarousel('next', false);
					}.bind(this));

					this.gallery.on('click', 'img', function (event) {
						var target = $(event.target).parents('li')[0];
						this.loadCurrentSlide(target);
					}.bind(this));

					this.element.on('click', '.cl-prev-icon', function () {
						var target = this.gallery.find('li.current').prev('.visible')[0];
						if (target) {
							this.loadCurrentSlide(target);
						}
					}.bind(this));

					this.element.on('click', '.cl-next-icon', function () {
						var target = this.gallery.find('li.current').next('.visible')[0];
						if (target) {
							this.loadCurrentSlide(target);
						}
					}.bind(this));

					this.element.on('click', '.cl-play-icon', function () {
						this.handlePreviwPlayClick();
					}.bind(this));

					this.element.on('click', 'img.preview', function(event) {
						var startingIndex = this.gallery.find('li.current').attr('data-index');
						this.openPopup(startingIndex);
					}.bind(this));
					break;
				case 6:
					this.gallery.on('click', '.cl-carousel-prev-icon', function () {
						this.currentPage -= 1;
						if (this.currentPage < 1) {
							this.currentPage = 1;
						}
						this.calculatePossitions();
					}.bind(this));

					this.gallery.on('click', '.cl-carousel-next-icon', function () {
						this.currentPage += 1;
						if (this.currentPage > this.gallery.find('li.visible').length/this.options.count) {
							this.currentPage = Math.floor(this.gallery.find('li.visible').length/this.options.count) + 1;
						}
						this.calculatePossitions();
					}.bind(this));
					this.element.on('click', filter_zoom, function(event) {
						var startingIndex = $(event.target).parents('li.visible').attr('data-index');
						this.openPopup(startingIndex);
					}.bind(this));


					this.element.find('div.cg_pages').on('click', 'span', function(event) {
						this.element.find('div.cg_pages>span').removeClass('selected');
						this.currentPage = $(event.target).text()*1;
						$(event.target).addClass('selected');
						this.calculatePossitions();
					}.bind(this));

					if (filter_link === '') {
						return;
					}
					this.element.on('click', filter_link, function(event) {
						var link = $(event.target).parents('li').find('img').attr('data-link');
						var target = $(event.target).parents('li').find('img').attr('data-target');
						if (link!=='') {
							window.open(link, target==='1' ? '_blank' : '_self');
						}
					}.bind(this));
					break;
				case 7:
				case 8:
				case 9:
					break;
			}
		}.bind(this);

		this.openPopup = function (startingIndex) {
			var imagesToShow = [];
			this.element.find("li.visible").each(function (index, el) {
				var currentEl = $(el);
				var currentImg = currentEl.find('img');
				var currentImage = {
					thumbnail : currentImg.attr('src'),
					path : currentImg.attr('data-path'),
					caption : currentImg.attr('data-description'),
					name : currentImg.attr('title')
				};
				imagesToShow.push(currentImage);
			});
			this.lightbox.open(imagesToShow, startingIndex);
		}.bind(this);

		this.showImage = function (el) {
			switch (this.options.view) {
				case 1:
				case 6:
				case 7:
				case 8:
				case 9:
				case 10:
					this.hideLoading(el.parents('li'));
					break;
				case 2:
				case 3:
				case 4:
				case 5:
					el.parents('li').attr('data-loaded', true);
					if (this.checkIfReadyToRecalculate()) {
						this.calculatePossitions();
						this.gallery.find('li.visible').each(function(index, el){
							this.hideLoading($(el));
						}.bind(this))
					}
					break;
			}
		}.bind(this);

		this.hideLoading = function (el) {
			el.find('div.cg-main-area-cover').hide();
		}.bind(this);

		this.hidePreviewLoading = function (el) {
			var cover = el.find('div.cg-main-area-cover');
			cover.css('opacity', 0);
			setTimeout(function() {
				cover.hide();
			}, 300);
		}.bind(this);

		this.showPreviewLoading = function (el) {
			var cover = el.find('div.cg-main-area-cover');
			cover.show();
			cover.css('opacity', 1);
		}.bind(this);

		this.checkIfReadyToRecalculate = function () {
			var ready = true;
			this.gallery.find('li.visible').not('.next-page').each(function (index, el) {
				if (!$(el).attr('data-loaded')) {
					ready = false;
				}
			});
			return ready;
		}.bind(this);

		this.checkIfThumbnailReady = function (el) {
			var imgType = 'weblink';
			if (el.hasClass('local')) {
				imgType = 'local';
			}
			var promise = new Promise(function(resolve, reject) {
				var url = this.options.mainpath + 'index.php?option=com_creativegallery&view=creativeajax&layout=thumbnailcreator&format=json&album_id=' + this.options.id + '&img_name=' + el.attr('data-path') + '&img_type=' + imgType;
				var request = $.ajax({
					url: url,
					method: 'GET',
					dataType: 'json'
				});
				request.done(function (data) {
					resolve(el);
				}.bind(this));
				request.fail(function (err) {
					// TODO implement error state (in beckend too)
					reject(el);
				}.bind(this));
			}.bind(this));
			promise.el = el;
			return promise;
		}.bind(this);

		this.checkIfimageLoaded = function (item, src) {
			item.removeAttr('complete');
			item.attr('src', src);

			var promise = new Promise(function(resolve, reject) {
				var imageLoadStatusCheck = this.options.imageLoadStatusCheck;
				var imageLoadingTimeout = this.options.imageLoadingTimeout;
				var checkIfLoaded = function (count) {
					count = count || 0;
					if (count*imageLoadStatusCheck > imageLoadingTimeout) {
						reject(item);
					}
					count ++;
					if (!item[0].complete) {
						setTimeout(function(){
							checkIfLoaded(count);
						}.bind(this), imageLoadStatusCheck);
						return;
					} else {
						resolve(item);
						return;
					}
				};
				checkIfLoaded();
			}.bind(this));
			promise.el = item;
			return promise;

		}.bind(this);


		/// Preview Options

		this.loadCurrentSlide = function (item) {
			$(item).addClass('current').siblings('li').removeClass('current');
			var imageToLoad = $(item).find('img').attr('data-path'),
				previewWrapper = this.element.find('div.preview-wrapper'),
				previewImage = previewWrapper.find('img');

			this.showPreviewLoading(previewWrapper);
			var loadingIndicator = this.element.find('div.preview-timer-inner');
			loadingIndicator.addClass('notransition').width(0);
			loadingIndicator[0].offsetWidth;

			var imageLoadPromise = this.checkIfimageLoaded(previewImage, imageToLoad);

			imageLoadPromise.then(function () {

				previewWrapper.find('.preview-timer').width(previewImage.width());
				previewWrapper.find('.preview-timer').css('top', (parseInt(previewImage.css('top'))-previewImage.height()/2));
				previewWrapper.find('.cg-main-area-cover').width(previewImage.width()+1);
				previewWrapper.find('.cg-main-area-cover').height(previewImage.height()+1);
				this.hidePreviewLoading(previewWrapper);
				this.moveCarousel('prev', true);
				if (this.currentSliding!=='') {
					this.startAutoPlay();
				}
			}.bind(this), function () {
				this.showImageLoadingError(previewImage);
			}.bind(this));
		}.bind(this);

		this.handlePreviwPlayClick = function () {
			if (this.element.find('.cl-play-icon').hasClass('cg_sprite-pause-32')) {
				this.element.find('.cl-play-icon').removeClass('cg_sprite-pause-32').addClass('cg_sprite-play-32');
				this.stopAutoPlay();
			} else {
				this.element.find('.cl-play-icon').removeClass('cg_sprite-play-32').addClass('cg_sprite-pause-32');
				this.startAutoPlay();
			}
		}.bind(this);

		this.startAutoPlay = function () {
			var currentSlidePromise = this.newAutoPlayPage();
			currentSlidePromise.then(function () {
				// Success
				var target = this.gallery.find('li.current').next('.visible')[0];
				if (target && this.currentSliding!=='') {
					this.loadCurrentSlide(target);
				}
			}.bind(this));
		}.bind(this);

		this.stopAutoPlay = function () {
			var loadingIndicator = this.element.find('div.preview-timer-inner');
			loadingIndicator.addClass('notransition').width(0);
			loadingIndicator[0].offsetWidth;
			loadingIndicator.removeClass('notransition');
			this.currentSliding = '';
		}.bind(this);

		this.newAutoPlayPage = function () {
			return new Promise(function (resolve, reject) {
				var loadingIndicator = this.element.find('div.preview-timer-inner');
				loadingIndicator.addClass('notransition').width(0);
				loadingIndicator[0].offsetWidth;
				loadingIndicator.removeClass('notransition').width('100%');
				var date = new Date();
				this.currentSliding = date;
				setTimeout(function () {
					if (this.currentSliding === date) {
						resolve();
					} else {
						reject();
					}
				}.bind(this), this.options.prev_speed * 1000);

			}.bind(this))
		}.bind(this);

		this.moveCarousel = function (direction, centralize) {
			var stepX = 0;
			var stepY = 0;

			var firstElementPredictedPossitionX = 0;
			var firstElementPredictedPossitionY = 0;
			var lastElementPredictedPossitionX = 0;
			var lastElementPredictedPossitionY = 0;
			if (!centralize) {
				switch (this.options.view) {
					case 4:
						stepX = this.gallery.width()/2 + this.options.margin;
						break;
					case 5:
						stepY = this.gallery.height()/2 + this.options.margin;
						break;
				}
				if (direction==='next') {
					stepX *= -1;
					stepY *= -1;
				}
			} else {
				var currentImage = $(this.gallery).find('li.current'),
					currentImageX = parseInt(currentImage.attr('data-left')),
					currentImageY = parseInt(currentImage.attr('data-top'));
					currentImageW = parseInt(currentImage.width());
					currentImageH = parseInt(currentImage.height());
				if (!isNaN(currentImageX) && currentImageX!==0) {
					stepX = (this.gallery.width() - currentImageW - 2*this.options.margin)/2 - currentImageX;
				}
				if (!isNaN(currentImageY) && currentImageY!==0) {
					stepY = (this.gallery.height() - currentImageH - 2*this.options.margin)/2 - currentImageY;
				}
			}
			var firstElement = this.gallery.find('li.visible').first();
			var lastElement = this.gallery.find('li.visible').last();


			firstElementPredictedPossitionX = parseInt(firstElement.attr('data-left')) + stepX;
			firstElementPredictedPossitionY = parseInt(firstElement.attr('data-top')) + stepY;

			var lastElementAllowedX;
			var lastElementAllowedY;

			lastElementAllowedX = $(this.gallery).width() - lastElement.width() - 2*this.options.margin;
			lastElementAllowedY = $(this.gallery).height() - lastElement.height() - 2*this.options.margin;

			lastElementPredictedPossitionX = parseInt(lastElement.attr('data-left')) + stepX;
			lastElementPredictedPossitionY = parseInt(lastElement.attr('data-top')) + stepY;

			if (firstElementPredictedPossitionX > 0) {
				stepX = (-1)*parseInt(firstElement.attr('data-left'));
			} else if (lastElementPredictedPossitionX < lastElementAllowedX) {
				stepX = lastElementAllowedX - parseInt(lastElement.attr('data-left'));
			}

			if (firstElementPredictedPossitionY > 0) {
				stepY = (-1)*parseInt(firstElement.attr('data-top'));
			} else if (lastElementPredictedPossitionY < lastElementAllowedY) {
				stepY = lastElementAllowedY - parseInt(lastElement.attr('data-top'));
			}

			this.gallery.find('li.visible').each(function(index, el) {
				$(el).css({
					top: parseInt($(el).attr('data-top')) + stepY,
					left: parseInt($(el).attr('data-left')) + stepX
				}).attr({
					'data-top': parseInt($(el).attr('data-top')) + stepY,
					'data-left': parseInt($(el).attr('data-left')) + stepX
				});
			});
		}.bind(this);
		this.init();
		return this;
	}


})(creativeSolutionsjQuery);