'use strict';
const path = require('path');
const gulp = require('gulp');
const sass = require('gulp-sass');

const PROJECT_DIR = path.resolve(__dirname);
const SASS_FILES = `${PROJECT_DIR}/profile/static/sass/**/*.scss`;
const CSS_DIR = `${PROJECT_DIR}/profile/static/css`;

gulp.task('sass', function () {
  return gulp.src(SASS_FILES)
    .pipe(sass({
      outputStyle: 'expanded'
    }).on('error', sass.logError))
    .pipe(gulp.dest(CSS_DIR));
});

gulp.task('default', ['sass']);
