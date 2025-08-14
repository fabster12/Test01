(function ($) {
    window.DirectionAwareHover = function (options) {
        if (!options || !options.wrapper ) {
            return null;
        }
        this.wrapper = $(options.wrapper);
        this.init = function () {

            this.wrapper.find("ul.gallery").on('mouseenter', 'li.visible' , function(event) {
                //event.preventDefault();
                /* Act on the event */
                var direction = getDirection (this, event),
                    animSpeed = $(this).css('transitionDuration');
                switch (direction) {
                    case "top":
                        $(this).find("div.overlay").show().css({
                            top: 0 - $(this).height(),
                            left: 0
                        }).stop(true, true).animate({top: 0}, animSpeed, "swing",function(){
                            // //console.log("top");
                        });
                        break;
                    case "left":
                        $(this).find("div.overlay").show().css({
                            top: 0,
                            left: 0 - $(this).width()
                        }).stop(true, true).animate({left: 0}, animSpeed, "swing", function(){
                            // //console.log("left");
                        });
                        break;
                    case "right":
                        $(this).find("div.overlay").show().css({
                            top: 0,
                            left: $(this).width()
                        }).stop(true, true).animate({left: 0}, animSpeed, "swing", function(){
                            // //console.log("right");
                        });
                        break;
                    case "bottom":
                        $(this).find("div.overlay").show().css({
                            top: $(this).height(),
                            left: 0
                        }).stop(true, true).animate({top: 0}, animSpeed, "swing", function(){
                            // //console.log("bottom");
                        });
                        break;
                }
            });

            this.wrapper.find("ul.gallery").find("li.visible").on('mouseleave' , function(event) {
                //event.preventDefault();
                /* Act on the event */
                var direction = getDirection (this, event),
                    animSpeed = $(this).css('transitionDuration');
                switch (direction) {
                    case "top":
                        $(this).find("div.overlay").css({
                            top: 0,
                            left: 0
                        }).stop(true, true).animate({top: 0-$(this).height()}, animSpeed, "swing", function(){
                            // //console.log("top");
                            $(this).hide();
                        });
                        break;
                    case "left":
                        $(this).find("div.overlay").css({
                            top: 0,
                            left: 0
                        }).stop(true, true).animate({left: 0 - $(this).width()}, animSpeed, "swing", function(){
                            // //console.log("left");
                            $(this).hide();
                        });
                        break;
                    case "right":
                        $(this).find("div.overlay").css({
                            top: 0,
                            left: 0
                        }).stop(true, true).animate({left: $(this).width()}, animSpeed, "swing", function(){
                            // //console.log("right");
                            $(this).hide();
                        });
                        break;
                    case "bottom":
                        $(this).find("div.overlay").css({
                            top: 0,
                            left: 0
                        }).stop(true, true).animate({top: $(this).height()}, animSpeed, "swing", function(){
                            // //console.log("bottom");
                            $(this).hide();
                        });
                        break;
                }

            });
        }.bind(this);
        function getDirection (elem, event) {
            var position = $(elem).offset(),
                mouseX = parseInt(event.pageX),
                mouseY = parseInt(event.pageY),
                posLeft = parseInt(position.left),
                posTop = parseInt(position.top),
                posRight = posLeft + parseInt($(elem).width()),
                posBottom = posTop + parseInt($(elem).height()),
                offsetTop = Math.abs(posTop - mouseY),
                offsetLeft = Math.abs(posLeft - mouseX),
                offsetRight = Math.abs(posRight - mouseX),
                offsetBottom = Math.abs(posBottom - mouseY),
                min = Math.min(offsetTop, offsetLeft, offsetRight, offsetBottom);
            switch (min) {
                case offsetTop:
                    return "top";
                case offsetLeft:
                    return "left";
                case offsetRight:
                    return "right";
                case offsetBottom:
                    return "bottom";
            }
        }
        this.init();
        return this;
    }
})(creativeSolutionsjQuery);
