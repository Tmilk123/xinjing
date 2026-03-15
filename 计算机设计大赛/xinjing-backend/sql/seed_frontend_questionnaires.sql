SET NAMES utf8mb4;

START TRANSACTION;

-- 1) Ensure frontend template codes exist and are aligned with current app logic.
INSERT INTO questionnaire_templates (code, name, description, total_score_rule, is_active, created_at)
VALUES
  ('phq9', 'PHQ-9 抑郁初筛', '前端筛查页使用：PHQ-9，9题，0-3分', 'sum(9 questions, each 0-3), max 27', 1, NOW()),
  ('sds',  'SDS 抑郁自评量表', '前端筛查页使用：SDS，20题，1-4分（含反向计分）', 'raw_sum_with_reverse * 1.25, max 100', 1, NOW()),
  ('ais',  'AIS 失眠量表', '前端筛查页使用：AIS，8题，0-4分', 'sum(8 questions, each 0-4), max 32', 1, NOW()),
  ('pss',  'PSS 压力感知量表', '前端筛查页使用：PSS，10题，0-4分（含反向计分）', 'sum(10 questions with reverse items), max 40', 1, NOW())
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  description = VALUES(description),
  total_score_rule = VALUES(total_score_rule),
  is_active = VALUES(is_active);

-- 2) Rebuild question bank for these four templates to keep exact mapping with frontend.
DELETE qq
FROM questionnaire_questions AS qq
JOIN questionnaire_templates AS qt ON qt.id = qq.template_id
WHERE qt.code IN ('phq9', 'sds', 'ais', 'pss');

-- Shared options JSON per scale (copied from frontend ScreeningPage.vue).
-- PHQ-9 options: 0-3
SET @phq9_options = '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]';
SET @phq9_score   = '{"0":0,"1":1,"2":2,"3":3}';

-- SDS options: 1-4
SET @sds_options        = '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]';
SET @sds_score_normal   = '{"1":1,"2":2,"3":3,"4":4}';
SET @sds_score_reverse  = '{"1":4,"2":3,"3":2,"4":1}';

-- AIS options: 0-4
SET @ais_options = '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]';
SET @ais_score   = '{"0":0,"1":1,"2":2,"3":3,"4":4}';

-- PSS options: 0-4
SET @pss_options       = '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]';
SET @pss_score_normal  = '{"0":0,"1":1,"2":2,"3":3,"4":4}';
SET @pss_score_reverse = '{"0":4,"1":3,"2":2,"3":1,"4":0}';

INSERT INTO questionnaire_questions (
  template_id, question_no, question_text, question_type, options_json, score_mapping, created_at
)
VALUES
  -- PHQ-9 (9)
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 1, '做事时提不起劲儿或没有兴趣', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 2, '感到心情低落、沮丧或绝望', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 3, '入睡困难、睡不安稳或睡眠过多', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 4, '感觉疲倦或没有活力', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 5, '食欲不振或吃得太多', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 6, '觉得自己很糟、很失败，或让自己及家人失望', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 7, '对事物专注有困难，例如阅读报纸或看电视时', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 8, '动作或说话速度缓慢到别人已经察觉？或刚好相反，烦躁或坐立不安', 'single_choice', @phq9_options, @phq9_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'phq9'), 9, '有不如死掉或用某种方式伤害自己的念头', 'single_choice', @phq9_options, @phq9_score, NOW()),

  -- SDS (20), reverse items: 5,6,11,12,14,16,17,18,20
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 1, '我觉得情绪低落，郁闷', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 2, '我觉得一天中早晨心情最差', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 3, '我一阵阵哭出来或觉得想哭', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 4, '我晚上睡眠不好', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 5, '我吃得跟平常一样多', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 6, '我与异性密切接触时和以往一样感到愉快', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 7, '我发现我的体重在下降', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 8, '我有便秘的苦恼', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 9, '我心跳比平时快', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 10, '我无缘无故地感到疲乏', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 11, '我的头脑跟平常一样清楚', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 12, '我觉得做事情很容易', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 13, '我坐卧不安，难以保持平静', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 14, '我对未来抱有希望', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 15, '我比平时更容易激怒', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 16, '我觉得决定什么事很容易', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 17, '我觉得自己是个有用的人，有人需要我', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 18, '我的生活过得很有意义', 'single_choice', @sds_options, @sds_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 19, '我认为如果我死了别人会生活得更好', 'single_choice', @sds_options, @sds_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'sds'), 20, '平常感兴趣的事我仍然照样感兴趣', 'single_choice', @sds_options, @sds_score_reverse, NOW()),

  -- AIS (8)
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 1, '入睡时间（关灯后多久才能睡着）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 2, '夜间苏醒（夜里醒来次数多，难以再入睡）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 3, '比期望的时间早醒', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 4, '总睡眠时间（比平时明显减少）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 5, '总睡眠质量（无论睡多久，都觉得质量差）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 6, '白天情绪（睡眠不好影响情绪状态）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 7, '白天身体功能（精力、体力、注意力受影响）', 'single_choice', @ais_options, @ais_score, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'ais'), 8, '白天嗜睡（白天犯困、难以集中注意力）', 'single_choice', @ais_options, @ais_score, NOW()),

  -- PSS (10), reverse items: 4,5,7,8
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 1, '感到无法控制生活中重要的事情', 'single_choice', @pss_options, @pss_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 2, '感到无法处理堆积的所有事情', 'single_choice', @pss_options, @pss_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 3, '感到紧张不安或有压力', 'single_choice', @pss_options, @pss_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 4, '成功地处理了生活中的麻烦', 'single_choice', @pss_options, @pss_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 5, '感到事情正按自己的意愿发展', 'single_choice', @pss_options, @pss_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 6, '发现无法应对所有必须做的事情', 'single_choice', @pss_options, @pss_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 7, '能够控制生活中的烦恼', 'single_choice', @pss_options, @pss_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 8, '感到自己能掌控生活中的所有问题', 'single_choice', @pss_options, @pss_score_reverse, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 9, '因为事情超出控制而生气', 'single_choice', @pss_options, @pss_score_normal, NOW()),
  ((SELECT id FROM questionnaire_templates WHERE code = 'pss'), 10, '感到困难堆积如山，无法克服', 'single_choice', @pss_options, @pss_score_normal, NOW());

COMMIT;

-- Optional verification:
-- SELECT qt.code, qt.name, COUNT(*) AS question_count
-- FROM questionnaire_templates qt
-- JOIN questionnaire_questions qq ON qq.template_id = qt.id
-- WHERE qt.code IN ('phq9', 'sds', 'ais', 'pss')
-- GROUP BY qt.code, qt.name
-- ORDER BY qt.code;
