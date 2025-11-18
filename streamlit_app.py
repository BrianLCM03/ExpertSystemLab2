import streamlit as st
import logging

# 尝试导入 clips（如果不可用则在界面中提示）
try:
	import clips
	CLIPS_AVAILABLE = True
except Exception as _e:
	clips = None
	CLIPS_AVAILABLE = False


logging.basicConfig(level=logging.INFO, format="%(message)s")


def create_env():
	"""创建并返回一个 CLIPS 环境（如果可用）。"""
	env = clips.Environment()
	# LoggingRouter 在一些 clips 绑定中可用，用于捕获 CLIPS 日志
	try:
		router = clips.LoggingRouter()
		env.add_router(router)
	except Exception:
		# 如果不存在 LoggingRouter，忽略，不影响基本推理功能
		pass
	return env


st.title("Expert Systems LAB 2")

st.write("这个示例会把输入作为一个 fact 断言到 CLIPS，然后运行推理并显示结果。")

name = st.text_input("Enter your name")

if st.button("Run inference"):
	if not CLIPS_AVAILABLE:
		st.error("无法导入 'clips' 模块。请先安装 clips（例如：pip install clips 或根据你的环境安装绑定）。")
	else:
		# 创建环境并定义简单的模板
		env = create_env()
		# 定义一个模板来储存结果（仅包含一个 slot: name）
		env.build('(deftemplate result (slot name))')

		# 断言一个事实到工作记忆。这里我们用双引号包裹字符串以确保名字可以包含空格。
		if name and name.strip():
			fact_str = f'(result (name "{name}"))'
		else:
			fact_str = '(result (name "<no-name>"))'

		# assert_string 是 clips.Environment 的方法，用于断言事实文本
		try:
			env.assert_string(fact_str)
		except Exception as e:
			st.error(f"断言事实失败：{e}")
			raise

		# 运行推理引擎
		try:
			env.run()
		except Exception as e:
			st.error(f"运行 CLIPS 失败：{e}")
			raise

		# 收集结果并显示
		results = []
		try:
			for fact in env.facts():
				# 只收集模板名为 result 的事实
				try:
					template_name = fact.template.name
				except Exception:
					# 如果 fact 对象访问失败，跳过
					continue

				if template_name == 'result':
					# 以防不同绑定对 slot 访问方式不同，尝试多种方式获取 slot 值
					value = None
					try:
						value = fact['name']
					except Exception:
						try:
							# 有些实现可能使用属性访问
							value = getattr(fact, 'name', None)
						except Exception:
							value = None

					# 如果 value 是可迭代的（例如 CLIPS 回传的多值），尝试转换为字符串
					if value is None:
						results.append(str(fact))
					else:
						results.append(str(value))
		except Exception as e:
			st.error(f"读取事实失败：{e}")

		if results:
			st.success(f"结果: {results[0]}")
		else:
			st.info("没有找到任何结果。")
