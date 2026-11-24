from __future__ import annotations

from typing import Any, Dict

from paper_workflow_skill import BaseAgentExecutor


LONG_INTRO = "".join([
    "在关键核心技术攻关和高质量发展背景下，企业基础研究与长期资本配置之间的关系成为重要议题。"
    "现有研究多把耐心资本理解为能够缓解短期压力、支持长期投入的资本形态，但对其究竟在投资什么缺乏更深刻解释。"
    "如果耐心资本只是追逐已经显化的优质企业，那么它与基础研究之间的关系可能只是筛选结果，而非真正的治理作用。"
    "与此同时，吸收能力在既有文献中也常被模糊使用，既被当成知识基础，又被当成能力本身，还常常与外显行为结果混在一起。"
    "本文据此提出一个新的研究问题：耐心资本投资的究竟是企业已经形成的能力，还是企业将既有知识基础转化为未来创新能力的可能性。"
    "基于这一判断，本文将吸收能力界定为一种需要时间连续性、组织承诺和跨边界整合才能逐步形成的高阶组织能力。"
    "从这个视角看，耐心资本的重要性不只在于延长资金期限，更在于为能力形成过程提供稳定支持。"
    "因此，本文尝试从研究对象、理论逻辑和研究设计三个层面，重构耐心资本与企业基础研究之间的关系。"
] * 4)

LONG_THEORY = "".join([
    "本文认为，知识基础只是能力形成的前提，而不是能力本身。"
    "企业可能拥有丰富的技术积累与研发经验，但这些资源并不会自动转化为持续稳定的外部知识识别、整合和再利用能力。"
    "真正意义上的吸收能力，是企业将既有知识基础持续组织为未来问题识别与创新能力的高阶组织过程。"
    "由此，耐心资本真正投资的并非某个单一项目，而是企业的能力形成期权。"
    "如果这一逻辑成立，那么耐心资本应更倾向于进入知识基础较强、但现实吸收能力尚未充分显化的企业。"
    "耐心资本进入后，还应更可能推动这类企业形成现实吸收能力，并进一步转化为基础研究活动。"
] * 8)

LONG_DESIGN = "".join([
    "本文的研究设计遵循选择—生成—结果三段式逻辑。"
    "第一步识别耐心资本更倾向进入何种企业，重点区分知识基础与现实吸收能力。"
    "第二步检验耐心资本进入后是否促进现实吸收能力形成。"
    "第三步考察现实吸收能力是否进一步转化为基础研究结果。"
    "在变量测度上，本文分别构造知识基础、现实吸收能力、潜在吸收能力识别变量以及基础研究结果变量。"
    "在模型设定上，采用进入选择模型、能力形成模型和结果模型相互衔接，以确保经验识别与理论逻辑一致。"
] * 10)


class MockAgentExecutor(BaseAgentExecutor):
    def run(
        self,
        agent_id: str,
        role: str,
        prompt: str | None,
        inputs: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Check agents
        if agent_id == "A_N0_Check":
            missing = [k for k in ["user_goal", "research_idea_raw"] if not state.get(k)]
            return {"is_input_sufficient": len(missing) == 0, "missing_fields": missing, "reason": ""}
        if agent_id.endswith("_Check"):
            key_map = {
                "A_N1_Check": "ready_for_object_clarification",
                "A_N2_Check": "ready_for_tension_extraction",
                "A_N3_Check": "ready_for_concept_split",
                "A_N4_Check": "ready_for_causality",
                "A_N5_Check": "ready_for_literature_positioning",
                "A_N6_Check": "ready_for_introduction",
                "A_N7_Check": "ready_for_theory_hypotheses",
                "A_N8_Check": "ready_for_research_design",
                "A_N9_Check": "ready_for_stress_test",
            }
            return {key_map[agent_id]: True, "reason": "mock pass"}

        # Generate agents
        if agent_id == "A_N0_Generate":
            return {
                "research_theme": "耐心资本与企业能力形成",
                "surface_question": "耐心资本是否促进企业基础研究",
                "suspected_core_variables": ["耐心资本", "吸收能力", "知识基础", "基础研究"],
                "user_pain_points": ["旧框架过于依赖知识导向表述", "没有回答耐心资本到底在投什么"],
                "current_stage": "理论建构",
                "immediate_priority_questions": [
                    "耐心资本投资的是已实现能力还是能力形成期权",
                    "吸收能力究竟是知识基础、现实能力还是能力形成过程"
                ]
            }
        if agent_id == "A_N1_Generate":
            return {
                "surface_explanandum": "企业基础研究表现",
                "true_research_object": "企业吸收能力形成过程及其被耐心资本识别和支持的机制",
                "difference_statement": "前者是结果变量，后者是结果背后的能力形成对象。",
                "why_surface_is_insufficient": "只解释基础研究会把选择效应与能力生成混在一起。",
                "anchor_sentence": "本文真正研究的不是企业基础研究本身，而是耐心资本如何识别并支持企业吸收能力的形成过程。"
            }
        if agent_id == "A_N2_Generate":
            return {
                "core_question_1": "耐心资本到底在投什么，是已实现能力还是能力形成期权？",
                "core_question_2": "吸收能力到底是什么，是知识基础、现实能力还是一个形成过程？",
                "main_theoretical_tension": "筛选显性能力还是支持潜在能力生成",
                "excluded_side_issues": ["科学导向重构", "多重并列机制"]
            }
        if agent_id == "A_N3_Generate":
            return {
                "concepts": [
                    {
                        "name": "知识基础",
                        "ontological_type": "antecedent_resource_base",
                        "is_not": "不是吸收能力本身",
                        "antecedents": ["历史研发积累", "专利存量", "技术经验"],
                        "latent_form": "为能力形成提供原材料",
                        "realized_form": "通过组织过程转化为现实能力",
                        "observable_manifestations": ["研发资本存量", "发明专利存量"]
                    },
                    {
                        "name": "吸收能力",
                        "ontological_type": "organizational_capability",
                        "is_not": "不是单纯合作行为，也不是知识存量",
                        "antecedents": ["知识基础", "组织承诺", "持续研发"],
                        "latent_form": "具备形成能力的可能性但尚未显化",
                        "realized_form": "可持续识别、整合和再利用外部知识的现实能力",
                        "observable_manifestations": ["外部知识内化率", "后续内部再利用"]
                    }
                ]
            }
        if agent_id == "A_N4_Generate":
            return {
                "ex_ante_selection_logic": "耐心资本更可能识别知识基础较强且具有能力形成潜力的企业。",
                "ex_post_generation_logic": "耐心资本进入后通过更长周期支持潜在能力向现实吸收能力转化。",
                "primary_logic": "hybrid",
                "secondary_logic": "generation_after_selection",
                "causal_chain": [
                    "识别知识基础与能力形成潜力",
                    "支持现实吸收能力形成",
                    "基础研究作为能力形成结果出现"
                ],
                "one_sentence_thesis": "耐心资本投资的不是单一长期项目，而是企业把知识基础转化为未来创新能力的形成期权。"
            }
        if agent_id == "A_N5_Generate":
            return {
                "parent_literature": ["耐心资本与长期创新", "吸收能力理论", "能力形成与组织学习"],
                "nearest_neighbor_concepts": ["dynamic capability", "absorptive capacity", "patient capital"],
                "literature_gap": "现有研究没有同时解释耐心资本事前识别了什么，以及事后支持了什么能力形成过程。",
                "contribution_statement": "本文不是在重复长期资本支持长期研发，而是在回答长期资本如何识别并支持企业能力形成。",
                "non_contribution_warning": "若仅证明耐心资本与基础研究正相关，则贡献会退化为筛选优质企业。"
            }
        if agent_id == "A_N6_Generate":
            return {
                "full_text": LONG_INTRO,
                "paragraph_map": [
                    "现实问题与研究背景",
                    "现有文献局限",
                    "吸收能力概念混用问题",
                    "本文研究问题与贡献"
                ]
            }
        if agent_id == "A_N7_Generate":
            return {
                "full_text": LONG_THEORY,
                "hypotheses": [
                    {"id": "H1", "type": "selection", "statement": "耐心资本更倾向于进入知识基础较强的企业。"},
                    {"id": "H2", "type": "selection", "statement": "耐心资本更倾向于进入知识基础较强但现实吸收能力较弱的企业。"},
                    {"id": "H3", "type": "mediator", "statement": "耐心资本能够显著提升企业现实吸收能力。"},
                    {"id": "H4", "type": "main_effect", "statement": "现实吸收能力越强，企业越可能开展基础研究。"}
                ]
            }
        if agent_id == "A_N8_Generate":
            return {
                "full_text": LONG_DESIGN,
                "variable_map": [
                    {"concept": "知识基础", "variable_name": "KBase", "role": "antecedent", "measurement_logic": "折旧调整后的发明专利或研发资本存量"},
                    {"concept": "现实吸收能力", "variable_name": "RAC", "role": "mediator", "measurement_logic": "外部知识内化并被内部后续创新再利用的比率"},
                    {"concept": "基础研究", "variable_name": "Basic", "role": "outcome", "measurement_logic": "NPL发明专利、联合科研专利或论文产出"}
                ],
                "model_map": [
                    {"model_id": "M1", "model_purpose": "选择模型", "dependent_variable": "PatEntry", "key_independent_variables": ["KBase", "RAC", "LatentAC"]},
                    {"model_id": "M2", "model_purpose": "能力形成模型", "dependent_variable": "RAC", "key_independent_variables": ["PatCap", "PatCap×LatentAC"]},
                    {"model_id": "M3", "model_purpose": "结果模型", "dependent_variable": "Basic", "key_independent_variables": ["RAC", "PatCap"]}
                ]
            }
        if agent_id == "A_N9_Generate":
            return {
                "top_3_criticisms": [
                    "知识基础与现实吸收能力的经验区分仍需更强测度支撑。",
                    "耐心资本进入的外生性识别仍需更严格的供给侧工具变量。",
                    "基础研究结果变量仍可能部分反映科学合作而非真正能力形成。"
                ],
                "failure_layer_map": [
                    {"criticism": "概念区分仍可更清晰", "failure_node": "N3_Concept", "rollback_node": "N3_Concept"},
                    {"criticism": "识别策略需加强", "failure_node": "N8_ResearchDesign", "rollback_node": "N8_ResearchDesign"},
                    {"criticism": "结果变量界定可再收紧", "failure_node": "N8_ResearchDesign", "rollback_node": "N8_ResearchDesign"}
                ],
                "one_sentence_thesis": "耐心资本投资的不是已显化能力，而是企业将知识基础转化为未来创新能力的形成期权。",
                "pass_or_revise": "revise"
            }
        raise ValueError(f"Unknown agent_id: {agent_id}")
