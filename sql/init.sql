-- ============================================================
-- 个人博客系统 Web API 建表 SQL
-- 数据库：blog_db    字符集：utf8mb4
-- 使用方式：mysql -uroot -p < sql/init.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `blog_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `blog_db`;

-- ------------------------------------------------------------
-- 1. 用户表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `user` (
    `id`              INT          NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username`        VARCHAR(50)  NOT NULL                COMMENT '用户名',
    `email`           VARCHAR(100) NOT NULL                COMMENT '邮箱',
    `hashed_password` VARCHAR(100) NOT NULL                COMMENT '密码（bcrypt 加密，不存明文）',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_username` (`username`),
    UNIQUE KEY `uk_user_email` (`email`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';

-- ------------------------------------------------------------
-- 2. 分类表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `category` (
    `id`         INT         NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `name`       VARCHAR(50) NOT NULL                COMMENT '分类名称',
    `created_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_category_name` (`name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '分类表';

-- ------------------------------------------------------------
-- 3. 文章表（核心表）
--    user_id     → 删除用户时，级联删除其文章（CASCADE）
--    category_id → 删除分类时，文章保留、分类置空（SET NULL）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `article` (
    `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '文章ID',
    `title`       VARCHAR(200) NOT NULL                COMMENT '标题',
    `content`     TEXT         NOT NULL                COMMENT '内容',
    `user_id`     INT          NOT NULL                COMMENT '作者ID',
    `category_id` INT          NULL                    COMMENT '分类ID',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_article_title` (`title`),
    KEY `idx_article_user_category` (`user_id`, `category_id`),
    CONSTRAINT `fk_article_user`     FOREIGN KEY (`user_id`)     REFERENCES `user` (`id`)     ON DELETE CASCADE,
    CONSTRAINT `fk_article_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE SET NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '文章表';

-- ------------------------------------------------------------
-- 4. 评论表
--    article_id → 删除文章时，级联删除其评论（CASCADE）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `comment` (
    `id`         INT          NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    `content`    VARCHAR(500) NOT NULL                COMMENT '评论内容',
    `article_id` INT          NOT NULL                COMMENT '文章ID',
    `user_id`    INT          NOT NULL                COMMENT '评论人ID',
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
    PRIMARY KEY (`id`),
    KEY `idx_comment_article` (`article_id`),
    CONSTRAINT `fk_comment_article` FOREIGN KEY (`article_id`) REFERENCES `article` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_user`    FOREIGN KEY (`user_id`)    REFERENCES `user` (`id`)    ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '评论表';
